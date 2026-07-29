"""Computation traces.

Every CapEngine result carries a trace: an ordered list of named steps with exact dollar
values. The trace is what makes verified-synthetic data generation possible --

    1. CapEngine computes the answer and records each step.
    2. A frontier model writes natural prose from the trace.
    3. The verifier re-extracts every dollar figure from the prose and checks that each one
       appears in the trace.

Prose containing a number the engine never computed is rejected. That is the whole
anti-hallucination mechanism, so traces must record *every* quantity worth stating.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def usd(amount: int) -> str:
    """Format a whole-dollar integer the way cap sheets do: $12,345,678."""
    return f"${amount:,}"


@dataclass(frozen=True)
class Step:
    label: str
    value: int | None = None
    detail: str = ""

    def __str__(self) -> str:
        parts = [self.label]
        if self.value is not None:
            parts.append(f"= {usd(self.value)}")
        if self.detail:
            parts.append(f"({self.detail})")
        return " ".join(parts)


@dataclass
class Trace:
    steps: list[Step] = field(default_factory=list)

    def add(self, label: str, value: int | None = None, detail: str = "") -> None:
        self.steps.append(Step(label=label, value=value, detail=detail))

    def extend(self, other: Trace, prefix: str = "") -> None:
        for step in other.steps:
            label = f"{prefix}{step.label}" if prefix else step.label
            self.steps.append(Step(label=label, value=step.value, detail=step.detail))

    def values(self) -> set[int]:
        """Every dollar figure the engine actually computed -- the verifier's whitelist."""
        return {s.value for s in self.steps if s.value is not None}

    def render(self) -> str:
        return "\n".join(f"  {i + 1}. {s}" for i, s in enumerate(self.steps))

    def __str__(self) -> str:
        return self.render()
