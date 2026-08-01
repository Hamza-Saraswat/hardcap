"""Tests for template narration and the roster invariants it depends on."""

import random

import pytest

from capengine.models import Contract, Team
from datagen.narrate import NARRATORS, narrate
from datagen.scenarios import MIX, random_team, sample
from datagen.verify import verify


@pytest.mark.parametrize("seed", range(40))
def test_narration_always_survives_the_verifier(seed):
    """Templates may only restate figures the engine computed."""
    rng = random.Random(seed)
    scenario = sample(rng)
    result = verify(scenario, narrate(scenario, rng))
    assert result.ok, f"{scenario.kind}: {result.problems()}"


def test_every_scenario_type_has_a_narrator():
    assert set(NARRATORS) == set(MIX)


@pytest.mark.parametrize("kind", sorted(MIX))
def test_each_narrator_produces_substantial_prose(kind):
    rng = random.Random(3)
    scenario = sample(rng, kind=kind)
    text = narrate(scenario, rng)
    assert len(text) > 200, f"{kind} narration is too thin"
    # Most answers quote figures; a draft-penalty answer is about picks, not money.
    if kind != "draft_penalty":
        assert "$" in text


def test_rosters_never_contain_duplicate_names():
    """Two players sharing a name makes a trade scenario ambiguous about whose salary moves.

    This surfaced as verifier failures: `Team.find` returned the first match for both legs
    of an aggregated trade, so the outgoing total was wrong.
    """
    rng = random.Random(0)
    for _ in range(200):
        team = random_team(rng)
        names = [c.player for c in team.contracts]
        assert len(names) == len(set(names))


def test_generated_salaries_are_legal_contracts():
    """No contract may exceed the 35% maximum or fall below the minimum.

    A roster carrying an impossible salary discredits the example even when the rules
    reasoning applied to it is correct.
    """
    rng = random.Random(0)
    for _ in range(300):
        team = random_team(rng)
        k = team.constants
        for contract in team.contracts:
            assert contract.salary <= k.max_salary_35, (
                f"{contract.player} at ${contract.salary:,} exceeds the "
                f"${k.max_salary_35:,} maximum"
            )
            assert contract.salary >= k.minimum_salary(2) - 1


def test_generated_payroll_hits_its_target_tier():
    """Clamping salaries must not knock a team out of the apron tier it was built for."""
    from capengine.models import ApronLevel

    rng = random.Random(1)
    for level in ApronLevel:
        for _ in range(40):
            assert random_team(rng, level=level).apron_level is level


def test_find_refuses_an_ambiguous_name():
    team = Team(
        name="Ambiguous",
        contracts=[
            Contract(player="Same Name", salary=10_000_000),
            Contract(player="Same Name", salary=20_000_000),
        ],
    )
    with pytest.raises(KeyError, match="appears 2 times"):
        team.find("Same Name")


def test_narration_varies_between_examples():
    """Identical phrasing on every example would teach the model to be repetitive."""
    rng = random.Random(11)
    openings = set()
    for _ in range(40):
        scenario = sample(rng, kind="trade_legality")
        openings.add(narrate(scenario, rng).split(".")[1].strip())
    assert len(openings) >= 4, "template variety is too low"
