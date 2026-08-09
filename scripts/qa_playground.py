"""End-to-end QA for the playground, run before anyone gets a link.

    python scripts/qa_playground.py --url http://127.0.0.1:7000 --passcode test123

Exercises the real HTTP path a tester would take -- not the model in isolation -- across
every question shape, the upload flow, multi-turn follow-ups, concurrency, and the guards.
Prints a pass/fail table and exits nonzero if anything a tester would hit is broken.

Deliberately checks behavior rather than answer quality: quality is what the eval harness
measures. This asks whether the thing works when five people poke it at once.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

TIMEOUT = 600


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""
    seconds: float = 0.0


def request(url: str, path: str, payload: dict | None = None,
            passcode: str = "", method: str = "POST",
            raw_body: bytes | None = None, content_type: str | None = None):
    headers = {}
    if passcode:
        headers["x-passcode"] = passcode
    if payload is not None:
        raw_body = json.dumps(payload).encode()
        content_type = "application/json"
    if content_type:
        headers["Content-Type"] = content_type

    req = urllib.request.Request(
        url.rstrip("/") + path, data=raw_body, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read())
        except Exception:  # noqa: BLE001 -- non-JSON error body is still a result
            return exc.code, {}


def ask(url: str, passcode: str, question: str, context: str = "",
        history: list[dict] | None = None) -> tuple[int, dict, float]:
    messages = list(history or []) + [{"role": "user", "content": question}]
    started = time.time()
    status, body = request(url, "/api/chat", {"context": context, "messages": messages},
                           passcode)
    return status, body, time.time() - started


def multipart(field: str, filename: str, data: bytes) -> tuple[bytes, str]:
    boundary = "----hardcapqa"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def run(url: str, passcode: str) -> list[Check]:
    checks: list[Check] = []

    status, body = request(url, "/api/health", method="GET")
    checks.append(Check("health endpoint", status == 200 and body.get("ok"),
                        f"model={body.get('model')}"))

    # A rules question with no cap sheet -- the shape that used to loop.
    status, body, secs = ask(url, passcode,
                             "Can a team over the second apron send cash in a trade?")
    answer = body.get("answer", "")
    looped = _looks_like_a_loop(answer)
    checks.append(Check("rules question, no cap sheet",
                        status == 200 and len(answer) > 80 and not looped,
                        f"{len(answer)} chars" + (" LOOPED" if looped else ""), secs))

    # Enumeration with no sheet -- v1's worst failure.
    status, body, secs = ask(url, passcode,
                             "Which exceptions does a first-apron team lose, and which does "
                             "it keep?")
    answer = body.get("answer", "")
    looped = _looks_like_a_loop(answer)
    checks.append(Check("enumeration, no cap sheet (v1 loop case)",
                        status == 200 and not looped and len(answer) > 80,
                        "LOOPED" if looped else f"{len(answer)} chars", secs))

    # Asked about a team with nothing pasted -- should ask, not invent.
    status, body, secs = ask(url, passcode, "Are the Nuggets over the second apron?")
    answer = body.get("answer", "").lower()
    asks = any(p in answer for p in ("cap sheet", "send me", "i need", "paste", "provide"))
    checks.append(Check("missing data -> asks rather than invents", status == 200 and asks,
                        "" if asks else "did not ask for the sheet", secs))

    # Arithmetic with a sheet, expecting tool use.
    sheet = (
        "2026-27 LEAGUE THRESHOLDS\n  Luxury tax line: $200,428,000\n"
        "  Tax bracket width: $6,064,000\n\nTEAM -- 2026-27\n"
        "| Player | Salary |\n| --- | ---: |\n| A | $120,000,000 |\n| B | $95,000,000 |\n\n"
        "Roster count: 2"
    )
    status, body, secs = ask(url, passcode, "What's our luxury tax bill? Show the brackets.",
                             sheet)
    checks.append(Check("tax question with a sheet", status == 200 and body.get("answer"),
                        f"calculator used {body.get('tool_calls', 0)}x", secs))

    # Multi-turn follow-up.
    history = [
        {"role": "user", "content": "Can a second-apron team aggregate salaries?"},
        {"role": "assistant", "content": "No. Aggregation is barred over the second apron."},
    ]
    status, body, secs = ask(url, passcode, "And what about sending cash?", "", history)
    checks.append(Check("multi-turn follow-up", status == 200 and len(body.get("answer", "")) > 40,
                        "", secs))

    # Upload path.
    data, ctype = multipart("file", "sheet.csv", b"player,salary\nJokic,59033114\n")
    status, body = request(url, "/api/upload", passcode=passcode, raw_body=data,
                           content_type=ctype)
    checks.append(Check("CSV upload extracts text",
                        status == 200 and "59033114" in body.get("text", "")))

    # Guards.
    status, _ = request(url, "/api/chat",
                        {"messages": [{"role": "user", "content": "hi"}]}, passcode="wrong")
    checks.append(Check("wrong passcode rejected", status == 401))

    status, body = request(url, "/api/feedback",
                           {"id": "qa", "rating": "down", "comment": "qa run"}, passcode)
    checks.append(Check("feedback recorded", status == 200))

    # Five testers at once, which is the realistic sharing scenario.
    started = time.time()
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [
            pool.submit(ask, url, passcode, "What is the second apron?")
            for _ in range(5)
        ]
        results = [f.result() for f in futures]
    ok = all(status == 200 and body.get("answer") for status, body, _ in results)
    checks.append(Check("5 concurrent users", ok,
                        f"slowest {max(r[2] for r in results):.0f}s",
                        time.time() - started))

    return checks


def _looks_like_a_loop(text: str, window: int = 6, threshold: int = 4) -> bool:
    words = text.split()
    if len(words) < window * 2:
        return False
    counts: dict[str, int] = {}
    for i in range(len(words) - window):
        gram = " ".join(words[i:i + window])
        counts[gram] = counts.get(gram, 0) + 1
    return max(counts.values()) >= threshold


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:7000")
    parser.add_argument("--passcode", default="")
    args = parser.parse_args()

    print(f"QA against {args.url}\n")
    checks = run(args.url, args.passcode)

    width = max(len(c.name) for c in checks) + 2
    for check in checks:
        mark = "PASS" if check.ok else "FAIL"
        timing = f"{check.seconds:6.1f}s" if check.seconds else "        "
        print(f"  [{mark}] {check.name:<{width}} {timing}  {check.detail}")

    failed = [c for c in checks if not c.ok]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed")
    if failed:
        print("Not ready to share. Failing: " + ", ".join(c.name for c in failed))
        sys.exit(1)
    print("Playground QA green.")


if __name__ == "__main__":
    main()
