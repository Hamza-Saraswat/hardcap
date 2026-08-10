"""Tests for the tool-calling agent loop.

The loop is scored-path code: if it mishandles a call, the eval blames the model for a
harness bug. So both call formats are exercised, along with the failure modes -- unknown
tools, bad expressions, and a model that never stops calling.
"""

import json

from eval.agent_loop import AgentTurn, parse_calls, run, strip_calls


def scripted(*responses):
    """A send() that replays a fixed list of assistant messages."""
    queue = list(responses)
    seen = []

    def send(messages, tools):
        seen.append(list(messages))
        return queue.pop(0) if queue else {"content": "done"}

    send.seen = seen
    return send


def test_parses_structured_tool_calls_with_dict_arguments():
    message = {"content": "", "tool_calls": [
        {"function": {"name": "calc", "arguments": {"expression": "2+2"}}}]}
    assert parse_calls(message) == [{"name": "calc", "arguments": {"expression": "2+2"}}]


def test_parses_structured_tool_calls_with_json_string_arguments():
    """Servers vary; the OpenAI convention sends arguments as a JSON string."""
    message = {"content": "", "tool_calls": [
        {"function": {"name": "calc", "arguments": json.dumps({"expression": "3*3"})}}]}
    assert parse_calls(message)[0]["arguments"] == {"expression": "3*3"}


def test_parses_raw_xml_calls_from_the_chat_template():
    """When the server does not parse calls, they arrive as template text."""
    message = {"content": (
        "<tool_call>\n<function=calc>\n<parameter=expression>\n6064000 * 1.25\n"
        "</parameter>\n</function>\n</tool_call>"
    )}
    calls = parse_calls(message)
    assert calls == [{"name": "calc", "arguments": {"expression": "6064000 * 1.25"}}]


def test_strip_calls_removes_raw_syntax_from_the_answer():
    text = "Here it is <tool_call>\n<function=calc>\n</function>\n</tool_call> and the rest."
    assert "<tool_call>" not in strip_calls(text)


def test_runs_a_call_and_returns_the_final_answer():
    send = scripted(
        {"content": "", "tool_calls": [
            {"function": {"name": "calc", "arguments": {"expression": "6064000 * 1.25"}}}]},
        {"content": "The bracket costs $7,580,000."},
    )
    turn = run(send, [{"role": "user", "content": "compute it"}])
    assert turn.final_text == "The bracket costs $7,580,000."
    assert turn.used_tools
    assert turn.tool_calls[0]["result"] == "7,580,000"
    assert not turn.hit_limit


def test_tool_result_is_fed_back_into_the_conversation():
    send = scripted(
        {"content": "", "tool_calls": [
            {"function": {"name": "calc", "arguments": {"expression": "2+2"}}}]},
        {"content": "It is 4."},
    )
    run(send, [{"role": "user", "content": "q"}])
    second_call_messages = send.seen[1]
    assert second_call_messages[-1]["role"] == "tool"
    assert second_call_messages[-1]["content"] == "4"


def test_answer_without_tools_passes_straight_through():
    turn = run(scripted({"content": "No arithmetic needed."}),
               [{"role": "user", "content": "explain the apron"}])
    assert turn.final_text == "No arithmetic needed."
    assert not turn.used_tools
    assert turn.rounds == 1


def test_bad_expression_comes_back_as_an_error_the_model_can_read():
    send = scripted(
        {"content": "", "tool_calls": [
            {"function": {"name": "calc", "arguments": {"expression": "5 / 0"}}}]},
        {"content": "That did not work."},
    )
    turn = run(send, [{"role": "user", "content": "q"}])
    assert turn.tool_calls[0]["result"].startswith("error:")
    assert turn.final_text == "That did not work."


def test_unknown_tool_is_reported_not_executed():
    send = scripted(
        {"content": "", "tool_calls": [
            {"function": {"name": "rm_rf", "arguments": {"path": "/"}}}]},
        {"content": "ok"},
    )
    turn = run(send, [{"role": "user", "content": "q"}])
    assert "unknown tool" in turn.tool_calls[0]["result"]


def test_endless_calling_hits_the_limit_and_says_so():
    """A model stuck in a call loop must surface as a failure, not a silent answer."""
    forever = {"content": "", "tool_calls": [
        {"function": {"name": "calc", "arguments": {"expression": "1+1"}}}]}
    send = scripted(*[forever] * 12)
    turn = run(send, [{"role": "user", "content": "q"}], max_rounds=4)
    assert turn.hit_limit
    assert turn.rounds == 4
    assert isinstance(turn, AgentTurn)


def test_followup_sends_arguments_as_a_json_string_not_a_dict():
    """The API and the chat template want opposite formats for the same field.

    vLLM validates `arguments` as a string and rejects a dict with a 422/400; the chat
    template iterates it as a mapping and silently renders no parameters given a string.
    Getting this backwards fails only on the loop's second round, so a single-shot test
    would have passed while the whole eval died.
    """
    send = scripted(
        {"content": "", "tool_calls": [
            {"function": {"name": "calc", "arguments": {"expression": "2+2"}}}]},
        {"content": "It is 4."},
    )
    run(send, [{"role": "user", "content": "q"}])
    followup = send.seen[1]
    assistant = next(m for m in followup if m.get("tool_calls"))
    arguments = assistant["tool_calls"][0]["function"]["arguments"]
    assert isinstance(arguments, str), "the API rejects a dict here"
    assert json.loads(arguments) == {"expression": "2+2"}
