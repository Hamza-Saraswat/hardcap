"""Playground backend: multi-turn chat, calculator tool use, and file upload.

    uv run uvicorn serving.app:app --host 0.0.0.0 --port 7000

Built and hardened against the Spark's own vLLM first; the same app later points at a hosted
endpoint by changing MODEL_BASE_URL. Nothing here assumes where the model lives.

Design notes worth knowing:

  - The calculator runs *server-side*, inside the agent loop. A tester's browser never
    executes anything, and the model cannot reach past `capengine.calc`'s AST evaluator.
  - Uploaded files are converted to text and shown back to the tester before being sent.
    The whole architecture is "fine-tune supplies the rules, context supplies the figures",
    so the context has to be visible, not magic.
  - Every exchange is logged as JSONL. Tester feedback is eval data, not anecdotes, and
    `eval/error_analysis.py` reads this format directly.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from datagen.prompts import SYSTEM_PROMPT
from eval import agent_loop
from eval.harness import post_chat

MODEL_BASE_URL = os.environ.get("MODEL_BASE_URL", "http://localhost:8000/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "capologist")
PASSCODE = os.environ.get("PLAYGROUND_PASSCODE", "")
LOG_PATH = Path(os.environ.get("PLAYGROUND_LOG", "logs/playground.jsonl"))

MAX_UPLOAD_BYTES = 2_000_000
MAX_CONTEXT_CHARS = 24_000
MAX_TURNS = 24
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 300

app = FastAPI(title="hardcap playground")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

_requests: dict[str, deque[float]] = defaultdict(deque)


class Turn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Turn] = Field(default_factory=list)
    context: str = ""


def check_passcode(supplied: str | None) -> None:
    if PASSCODE and supplied != PASSCODE:
        raise HTTPException(status_code=401, detail="Invalid or missing passcode.")


def check_rate_limit(who: str) -> None:
    """Keep one enthusiastic tester from starving everyone else on a single GPU."""
    now = time.time()
    seen = _requests[who]
    while seen and now - seen[0] > RATE_LIMIT_WINDOW_SECONDS:
        seen.popleft()
    if len(seen) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Rate limit: {RATE_LIMIT_REQUESTS} messages per "
                f"{RATE_LIMIT_WINDOW_SECONDS // 60} minutes. Give it a moment."
            ),
        )
    seen.append(now)


def log(event: str, payload: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as handle:
        handle.write(json.dumps({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "event": event,
            **payload,
        }, ensure_ascii=False) + "\n")


def extract_text(filename: str, raw: bytes) -> str:
    """Turn an uploaded cap sheet into text the model can read."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        try:
            import io

            from pypdf import PdfReader
        except ImportError:
            raise HTTPException(
                status_code=500, detail="PDF support needs pypdf installed on the server."
            ) from None
        try:
            reader = PdfReader(io.BytesIO(raw))
        except Exception:
            raise HTTPException(status_code=400, detail="Could not read that PDF.") from None
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()

    try:
        return raw.decode("utf-8", errors="replace").strip()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read that file.") from None


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "model": MODEL_NAME, "passcode_required": bool(PASSCODE)}


@app.post("/api/upload")
async def upload(
    file: UploadFile = File(...),
    x_passcode: str | None = Header(default=None),
) -> dict:
    check_passcode(x_passcode)
    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is larger than 2 MB.")

    text = extract_text(file.filename or "upload.txt", raw)
    if not text:
        raise HTTPException(
            status_code=400,
            detail="No text found. Scanned PDFs need OCR; paste the sheet instead.",
        )

    truncated = len(text) > MAX_CONTEXT_CHARS
    text = text[:MAX_CONTEXT_CHARS]
    log("upload", {"filename": file.filename, "chars": len(text), "truncated": truncated})
    # Returned for display, not silently injected -- the tester should see exactly what the
    # model will read.
    return {"filename": file.filename, "text": text, "truncated": truncated}


@app.post("/api/chat")
def chat(request: ChatRequest, x_passcode: str | None = Header(default=None)) -> dict:
    check_passcode(x_passcode)
    check_rate_limit(x_passcode or "anonymous")

    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages.")
    turns = [t for t in request.messages if t.role in {"user", "assistant"}][-MAX_TURNS:]
    if not turns or turns[-1].role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from the user.")

    conversation: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for index, turn in enumerate(turns):
        content = turn.content
        # Context rides with the first user turn so follow-ups stay short.
        if index == 0 and turn.role == "user" and request.context.strip():
            content = f"{request.context.strip()}\n\n{content}"
        conversation.append({"role": turn.role, "content": content})

    def send(messages, tools):
        return post_chat(MODEL_BASE_URL, MODEL_NAME, messages, tools,
                         disable_thinking=True)

    started = time.time()
    try:
        result = agent_loop.run(send, conversation)
    except Exception as exc:  # noqa: BLE001 -- surface transport failures as clean HTTP
        log("error", {"detail": str(exc)[:400]})
        raise HTTPException(
            status_code=503, detail="The model is not reachable right now."
        ) from None

    exchange_id = str(uuid.uuid4())[:8]
    log("chat", {
        "id": exchange_id,
        "question": turns[-1].content[:2000],
        "context_chars": len(request.context),
        "answer": result.final_text[:4000],
        "tool_calls": result.tool_calls,
        "hit_tool_limit": result.hit_limit,
        "seconds": round(time.time() - started, 1),
    })
    return {
        "id": exchange_id,
        "answer": result.final_text,
        # Count for the UI badge; the full expressions stay in the log, where error
        # analysis can read what the model actually asked the calculator.
        "tool_calls": len(result.tool_calls),
        "hit_tool_limit": result.hit_limit,
    }


class Feedback(BaseModel):
    id: str = ""
    rating: str = ""
    comment: str = ""


@app.post("/api/feedback")
def feedback(item: Feedback, x_passcode: str | None = Header(default=None)) -> dict:
    check_passcode(x_passcode)
    if item.rating not in {"up", "down", ""}:
        raise HTTPException(status_code=400, detail="rating must be up or down")
    log("feedback", {
        "id": item.id, "rating": item.rating, "comment": item.comment[:2000]
    })
    return {"ok": True}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(Path(__file__).parent / "chat.html")
