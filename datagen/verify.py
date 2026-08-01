"""The verifier -- the reason this dataset can be trusted.

Generated prose is accepted only if every dollar figure in it was computed by CapEngine or
pasted by the user. A sentence that invents a number, however plausible, is rejected and
regenerated. Without this step the dataset would teach the model to produce confident cap
figures that are subtly wrong, which is precisely the failure this project exists to avoid.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from datagen.scenarios import Scenario

# Only $-prefixed, comma-formatted figures count as claims about money. This deliberately
# ignores years ("2026-27"), counts, percentages, and per-dollar tax rates like $1.00.
_DOLLAR = re.compile(r"\$\s?([\d][\d,]*)(?:\.(\d+))?")
_APPROXIMATION = re.compile(
    r"\$\s?\d[\d,]*(?:\.\d+)?\s*(?:million|billion|M\b|B\b)|\babout \$|\broughly \$|~\$",
    re.IGNORECASE,
)


@dataclass
class Verification:
    ok: bool
    unknown_values: list[int] = field(default_factory=list)
    missing_required: list[int] = field(default_factory=list)
    approximations: list[str] = field(default_factory=list)
    verdict_ok: bool = True
    notes: list[str] = field(default_factory=list)

    def problems(self) -> str:
        lines = []
        if self.unknown_values:
            lines.append(
                "- These figures appear in your answer but were never computed: "
                + ", ".join(f"${v:,}" for v in self.unknown_values)
            )
        if self.missing_required:
            lines.append(
                "- These required figures are missing: "
                + ", ".join(f"${v:,}" for v in self.missing_required)
            )
        if self.approximations:
            lines.append(
                "- Rounded or abbreviated amounts are not allowed: "
                + ", ".join(self.approximations)
            )
        if not self.verdict_ok:
            lines.append("- The stated verdict does not match the computed one.")
        lines.extend(f"- {n}" for n in self.notes)
        return "\n".join(lines)


def dollar_figures(text: str) -> list[int]:
    """Every whole-dollar amount claimed in the text."""
    values = []
    for match in _DOLLAR.finditer(text):
        raw = match.group(1).replace(",", "")
        if not raw.isdigit():
            continue
        cents = match.group(2)
        # "$1.00 per dollar" is a tax rate, not an amount; skip sub-dollar decimals.
        if cents is not None and len(raw) <= 2:
            continue
        values.append(int(raw))
    return values


def verify(scenario: Scenario, response: str, strict_verdict: bool = True) -> Verification:
    """Check a generated answer against what the engine actually computed."""
    allowed = scenario.allowed_values()
    claimed = dollar_figures(response)

    unknown = sorted({v for v in claimed if v not in allowed and v >= 1000})
    missing = sorted({v for v in scenario.required_values if v not in claimed})
    approximations = sorted(set(_APPROXIMATION.findall(response)))

    verdict_ok = True
    if strict_verdict and scenario.verdict:
        verdict_ok = _verdict_matches(scenario.verdict, response)

    notes = []
    if len(response.strip()) < 120:
        notes.append("The answer is too short to have shown its work.")

    return Verification(
        ok=not unknown and not missing and not approximations and verdict_ok and not notes,
        unknown_values=unknown,
        missing_required=missing,
        approximations=approximations,
        verdict_ok=verdict_ok,
        notes=notes,
    )


_EXPLICIT_VERDICT = re.compile(
    r"verdict[:\s*]*\**\s*(legal|illegal|allowed|not allowed)", re.IGNORECASE
)


def _verdict_matches(verdict: str, response: str) -> bool:
    """Confirm the answer opens on the right side of a yes/no question.

    An explicit "**Verdict: LEGAL.**" line settles it outright. Only when one is missing do
    we fall back to scanning the opening for sentiment, and that fallback is deliberately
    narrow: over a wide window, bare substrings like "no," fire on innocuous clauses and
    flip a correct answer to a failure.
    """
    wants_negative = verdict.upper() in {"ILLEGAL", "NOT ALLOWED"}

    explicit = _EXPLICIT_VERDICT.search(response[:400])
    if explicit:
        stated_negative = explicit.group(1).lower() in {"illegal", "not allowed"}
        return stated_negative == wants_negative

    head = response[:200].lower()
    negative_markers = ("illegal", "not legal", "can't", "cannot", "not allowed", "blocked")
    positive_markers = ("legal", "allowed", "yes", "works", "can ")
    has_negative = any(m in head for m in negative_markers)
    has_positive = any(m in head for m in positive_markers)

    if wants_negative:
        return has_negative
    return has_positive and not has_negative
