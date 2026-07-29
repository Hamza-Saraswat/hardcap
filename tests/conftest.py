"""Shared fixtures for building teams at specific apron positions."""

from __future__ import annotations

import pytest

from capengine.models import Contract, Team


def contract(player: str, salary: int, **kwargs) -> Contract:
    return Contract(player=player, salary=salary, **kwargs)


def team_at(
    apron_salary: int,
    name: str = "Test Team",
    season: str = "2026-27",
    roster: int = 14,
    **kwargs,
) -> Team:
    """Build a team whose salary lands exactly on `apron_salary`.

    Salary is spread across `roster` contracts so roster-limit rules behave realistically,
    with the remainder loaded onto the first contract.
    """
    per_player = apron_salary // roster
    contracts = [contract(f"Player {i + 1}", per_player) for i in range(roster)]
    contracts[0] = contract("Player 1", per_player + apron_salary - per_player * roster)
    return Team(name=name, season=season, contracts=contracts, **kwargs)


def team_with(
    apron_salary: int,
    extras: list[Contract],
    name: str = "Test Team",
    season: str = "2026-27",
    roster: int = 12,
    **kwargs,
) -> Team:
    """Build a team sitting at exactly `apron_salary` that already includes `extras`.

    Use this whenever a scenario names specific players who are on the roster. Building a
    team at a target salary and then appending named contracts silently inflates it past
    the threshold you were trying to test.
    """
    filler = apron_salary - sum(c.apron_hit for c in extras)
    team = team_at(filler, name=name, season=season, roster=roster, **kwargs)
    team.contracts.extend(extras)
    return team


@pytest.fixture
def under_tax() -> Team:
    return team_at(150_000_000, name="Under Tax")


@pytest.fixture
def over_tax() -> Team:
    """Above the tax line but below the first apron."""
    return team_at(205_000_000, name="Over Tax")


@pytest.fixture
def over_first_apron() -> Team:
    """Between the first and second aprons."""
    return team_at(215_000_000, name="First Apron Team")


@pytest.fixture
def over_second_apron() -> Team:
    return team_at(230_000_000, name="Second Apron Team")
