"""Run a model turn that may call the calculator, and return the final answer.

A tool-using model does not answer in one shot: it emits a call, waits for the result, and
only then writes prose. Scoring the first response would grade an empty message with a
function call in it. This drives the exchange to completion and hands back the text a user
would actually see.

Two parsers, because a model that has just learned tool use will not always be tidy: the
structured `tool_calls` field servers return, and the raw XML the chat template emits when
the server does not parse it. Both are exercised in tests.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from capengine.calc import TOOL_SPEC, run_tool

MAX_TOOL_ROUNDS = 8

# The template's own call syntax, for when the server hands back raw text.
_XML_CALL = re.compile(
    r"<tool_call>\s*<function=(?P<name>\w+)>(?P<body>.*?)</function>\s*</tool_call>",
    re.DOTALL,
)
_XML_PARAM = re.compile(
    r"<parameter=(?P<key>\w+)>\s*(?P<value>.*?)\s*</parameter>", re.DOTALL
)


@dataclass
class AgentTurn:
    """What actually happened during one scored question."""

    final_text: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    rounds: int = 0
    hit_limit: bool = False

    @property
    def used_tools(self) -> bool:
        return bool(self.tool_calls)


def parse_calls(message: dict) -> list[dict]:
    """Extract calculator calls from a response, structured or raw."""
    calls = []
    for call in message.get("tool_calls") or []:
        function = call.get("function", {})
        arguments = function.get("arguments")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                # Some servers hand back a bare expression rather than JSON.
                arguments = {"expression": arguments}
        calls.append({"name": function.get("name", "calc"), "arguments": arguments or {}})

    if not calls:
        for match in _XML_CALL.finditer(message.get("content") or ""):
            arguments = {
                param.group("key"): param.group("value")
                for param in _XML_PARAM.finditer(match.group("body"))
            }
            calls.append({"name": match.group("name"), "arguments": arguments})
    return calls


def strip_calls(text: str) -> str:
    """Remove raw call syntax so it is not mistaken for the answer."""
    return _XML_CALL.sub("", text or "").strip()


def run(
    send,
    messages: list[dict],
    max_rounds: int = MAX_TOOL_ROUNDS,
) -> AgentTurn:
    """Drive a conversation to its final text answer.

    `send(messages, tools)` performs one model call and returns an assistant message dict.
    Keeping it injected means the harness, the playground, and the tests all exercise this
    same loop against different transports.
    """
    turn = AgentTurn()
    conversation = list(messages)

    for round_index in range(max_rounds):
        message = send(conversation, [TOOL_SPEC])
        calls = parse_calls(message)
        content = message.get("content") or ""

        if not calls:
            turn.final_text = strip_calls(content)
            turn.rounds = round_index + 1
            return turn

        conversation.append({
            "role": "assistant",
            "content": content,
            "tool_calls": [
                {
                    "id": f"call_{round_index}_{i}",
                    "type": "function",
                    "function": {"name": c["name"], "arguments": c["arguments"]},
                }
                for i, c in enumerate(calls)
            ],
        })
        for i, call in enumerate(calls):
            result = run_tool(call["arguments"]) if call["name"] == "calc" else (
                f"error: unknown tool {call['name']}"
            )
            turn.tool_calls.append({
                "expression": call["arguments"].get("expression", ""),
                "result": result,
            })
            conversation.append({
                "role": "tool",
                "tool_call_id": f"call_{round_index}_{i}",
                "name": call["name"],
                "content": result,
            })

    # Out of rounds. Report it rather than pretending the last text was an answer -- a model
    # stuck calling the calculator forever is a real failure worth seeing in the results.
    turn.hit_limit = True
    turn.rounds = max_rounds
    turn.final_text = strip_calls(content)
    return turn
