"""Tests for the playground backend.

This is the surface strangers will eventually touch, so the tests care as much about what
it refuses as what it does: oversized uploads, wrong passcodes, runaway request rates, and
a model server that is simply down.
"""

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("PLAYGROUND_PASSCODE", "letmein")
    monkeypatch.setenv("PLAYGROUND_LOG", str(tmp_path / "playground.jsonl"))
    import serving.app as app_module

    importlib.reload(app_module)
    return TestClient(app_module.app), app_module


def test_health_reports_the_model_and_that_a_passcode_is_required(client):
    api, _ = client
    body = api.get("/api/health").json()
    assert body["ok"] is True
    assert body["passcode_required"] is True


def test_chat_requires_the_passcode(client):
    api, _ = client
    response = api.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert response.status_code == 401


def test_chat_runs_the_agent_loop_and_returns_the_final_answer(client, monkeypatch):
    api, app_module = client

    calls = []

    def fake_send(base_url, model, messages, tools=None, disable_thinking=False):
        calls.append(messages)
        if len(calls) == 1:
            return {"content": "", "tool_calls": [
                {"function": {"name": "calc", "arguments": {"expression": "2+2"}}}]}
        return {"content": "It comes to $4."}

    monkeypatch.setattr(app_module, "post_chat", fake_send)
    response = api.post(
        "/api/chat",
        headers={"x-passcode": "letmein"},
        json={"messages": [{"role": "user", "content": "add it up"}]},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["answer"] == "It comes to $4."
    assert body["tool_calls"] == 1
    assert not body["hit_tool_limit"]


def test_context_rides_with_the_first_user_turn_only(client, monkeypatch):
    """Follow-ups should stay short rather than re-sending the whole cap sheet."""
    api, app_module = client
    seen = {}

    def fake_send(base_url, model, messages, tools=None, disable_thinking=False):
        seen["messages"] = messages
        return {"content": "Answer with enough length to look like a real reply here."}

    monkeypatch.setattr(app_module, "post_chat", fake_send)
    api.post(
        "/api/chat",
        headers={"x-passcode": "letmein"},
        json={
            "context": "DENVER CAP SHEET",
            "messages": [
                {"role": "user", "content": "first"},
                {"role": "assistant", "content": "reply"},
                {"role": "user", "content": "second"},
            ],
        },
    )
    contents = [m["content"] for m in seen["messages"]]
    assert any("DENVER CAP SHEET" in c and "first" in c for c in contents)
    assert "second" in contents[-1] and "DENVER CAP SHEET" not in contents[-1]


def test_last_message_must_be_from_the_user(client):
    api, _ = client
    response = api.post(
        "/api/chat",
        headers={"x-passcode": "letmein"},
        json={"messages": [{"role": "assistant", "content": "hello"}]},
    )
    assert response.status_code == 400


def test_unreachable_model_returns_503_not_a_stack_trace(client, monkeypatch):
    api, app_module = client

    def boom(*args, **kwargs):
        raise ConnectionError("connection refused")

    monkeypatch.setattr(app_module, "post_chat", boom)
    response = api.post(
        "/api/chat",
        headers={"x-passcode": "letmein"},
        json={"messages": [{"role": "user", "content": "hi"}]},
    )
    assert response.status_code == 503
    assert "not reachable" in response.json()["detail"]


def test_rate_limit_kicks_in(client, monkeypatch):
    api, app_module = client
    monkeypatch.setattr(app_module, "RATE_LIMIT_REQUESTS", 3)
    monkeypatch.setattr(
        app_module, "post_chat",
        lambda *a, **k: {"content": "A sufficiently long reply for the harness to accept."},
    )
    headers = {"x-passcode": "letmein"}
    payload = {"messages": [{"role": "user", "content": "hi"}]}
    codes = [api.post("/api/chat", headers=headers, json=payload).status_code
             for _ in range(5)]
    assert codes.count(429) >= 1


def test_upload_extracts_text_and_hands_it_back_for_display(client):
    api, _ = client
    response = api.post(
        "/api/upload",
        headers={"x-passcode": "letmein"},
        files={"file": ("sheet.csv", b"player,salary\nJokic,59033114\n", "text/csv")},
    )
    body = response.json()
    assert response.status_code == 200
    assert "59033114" in body["text"]
    assert body["truncated"] is False


def test_oversized_upload_is_refused(client, monkeypatch):
    api, app_module = client
    monkeypatch.setattr(app_module, "MAX_UPLOAD_BYTES", 10)
    response = api.post(
        "/api/upload",
        headers={"x-passcode": "letmein"},
        files={"file": ("big.txt", b"x" * 100, "text/plain")},
    )
    assert response.status_code == 413


def test_empty_file_is_refused_with_a_useful_message(client):
    api, _ = client
    response = api.post(
        "/api/upload",
        headers={"x-passcode": "letmein"},
        files={"file": ("blank.txt", b"   ", "text/plain")},
    )
    assert response.status_code == 400
    assert "paste" in response.json()["detail"].lower()


def test_feedback_is_recorded(client, tmp_path):
    api, app_module = client
    response = api.post(
        "/api/feedback",
        headers={"x-passcode": "letmein"},
        json={"id": "abc123", "rating": "down", "comment": "got the tax bill wrong"},
    )
    assert response.status_code == 200
    logged = app_module.LOG_PATH.read_text()
    assert "abc123" in logged and "got the tax bill wrong" in logged
