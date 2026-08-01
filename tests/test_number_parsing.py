"""Tests for the whitelist parser and verdict matching.

Both bugs covered here were found by writing agents working against the pipeline, not by
the test suite -- worth remembering that the verifier needs verifying too.
"""

import random

import pytest

from datagen.capsheet import cap_sheet
from datagen.scenarios import _numbers_in, random_team, sample
from datagen.verify import _verdict_matches


def test_csv_rows_do_not_produce_concatenated_garbage():
    """The bug: `[\\d,]+` swallowed CSV delimiters.

    "Achiuwa,3341192,0,1" parsed as the single value 334119201 -- a figure appearing
    nowhere on the cap sheet -- while the real salary was never whitelisted at all. That
    poisons the allowed set in both directions: correct salaries rejected, invented ones
    accepted.
    """
    parsed = _numbers_in("Marcus Achiuwa,3341192,0,1")
    assert 3_341_192 in parsed
    assert 334_119_201 not in parsed


def test_comma_grouped_figures_parse_as_one_number():
    assert _numbers_in("Salary cap: $164,961,000") == {164_961_000}


def test_mixed_formats_in_one_block():
    text = "| Luka Rees | $4,391,380 | -- | 1 |\nRees,4391380,0,1"
    assert 4_391_380 in _numbers_in(text)
    assert 439138001 not in _numbers_in(text)


@pytest.mark.parametrize("style", [0, 1, 2])
def test_every_cap_sheet_format_whitelists_its_own_salaries(style):
    """Markdown, plain columns, and CSV must all yield the salaries they display."""
    rng = random.Random(5)
    team = random_team(rng)
    parsed = _numbers_in(cap_sheet(team, style=style))
    for contract in team.contracts:
        assert contract.salary in parsed, (
            f"style {style} did not whitelist {contract.player}'s ${contract.salary:,}"
        )


@pytest.mark.parametrize("seed", range(20))
def test_scenario_whitelists_include_every_displayed_salary(seed):
    rng = random.Random(seed)
    scenario = sample(rng)
    allowed = scenario.allowed_values()
    for line in scenario.context.splitlines():
        for value in _numbers_in(line):
            assert value in allowed


# -- verdict matching -----------------------------------------------------------------------


def test_explicit_verdict_marker_settles_it():
    assert _verdict_matches("LEGAL", "**Verdict: LEGAL.** Anything at all here.")
    assert _verdict_matches("ILLEGAL", "**Verdict: ILLEGAL.** Anything at all here.")
    assert not _verdict_matches("LEGAL", "**Verdict: ILLEGAL.** Wrong side.")


def test_allowed_and_not_allowed_map_onto_the_same_axis():
    assert _verdict_matches("NOT ALLOWED", "**Verdict: ILLEGAL.** He earned too much.")
    assert _verdict_matches("ALLOWED", "**Verdict: LEGAL.** He is available.")
    assert _verdict_matches("NOT ALLOWED", "**Verdict: NOT ALLOWED.** Over the mid-level.")


def test_a_legal_answer_may_discuss_restrictions_after_the_marker():
    """With an explicit marker, later caveats cannot flip the verdict.

    Previously any "cannot" within 400 characters failed the answer, which pushed writers
    into contorting perfectly good explanations.
    """
    response = (
        "**Verdict: LEGAL.** The money works. Note that we cannot aggregate a second "
        "salary here, and taking back more would not be allowed either."
    )
    assert _verdict_matches("LEGAL", response)


def test_fallback_still_reads_plain_language_when_no_marker_is_present():
    assert _verdict_matches("ILLEGAL", "No, that trade cannot be processed as constructed.")
    assert _verdict_matches("LEGAL", "Yes, this works under the expanded bands.")
