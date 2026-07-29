"""Rendering teams and league constants as the tables a user would paste in.

The model is never meant to recall salary figures. It is meant to read them. So nearly every
training prompt carries a constants block and a cap sheet, formatted the way someone would
actually paste one out of capsheets.com or a spreadsheet, and the answer is derived from
those numbers alone.

Formats vary deliberately across the dataset -- markdown tables, plain columns, CSV -- so the
model learns to read a cap sheet rather than to pattern-match one particular layout.
"""

from __future__ import annotations

import random

from capengine.constants import SeasonConstants
from capengine.models import Team
from capengine.trace import usd


def constants_block(k: SeasonConstants) -> str:
    """The league-wide thresholds, as a front office would paste them at the top of a memo."""
    lines = [
        f"{k.season} LEAGUE THRESHOLDS",
        f"  Salary cap:          {usd(k.cap)}",
        f"  Luxury tax line:     {usd(k.tax_line)}",
        f"  First apron:         {usd(k.first_apron)}",
        f"  Second apron:        {usd(k.second_apron)}",
        f"  Non-taxpayer MLE:    {usd(k.non_taxpayer_mle)}",
        f"  Taxpayer MLE:        {usd(k.taxpayer_mle)}",
        f"  Room exception:      {usd(k.room_exception)}",
        f"  Tax bracket width:   {usd(k.tax_bracket_width)}",
    ]
    if k.bi_annual_exception is not None:
        lines.append(f"  Bi-annual exception: {usd(k.bi_annual_exception)}")
    return "\n".join(lines)


def _markdown_table(team: Team) -> str:
    rows = ["| Player | Salary | Unlikely incentives | Years left |",
            "| --- | ---: | ---: | ---: |"]
    for c in team.contracts:
        incentives = usd(c.incentives_unlikely) if c.incentives_unlikely else "--"
        rows.append(f"| {c.player} | {usd(c.salary)} | {incentives} | {c.years_remaining} |")
    return "\n".join(rows)


def _plain_columns(team: Team) -> str:
    width = max((len(c.player) for c in team.contracts), default=10) + 2
    rows = []
    for c in team.contracts:
        line = f"{c.player:<{width}}{usd(c.salary):>16}"
        if c.incentives_unlikely:
            line += f"   (+{usd(c.incentives_unlikely)} unlikely)"
        rows.append(line)
    return "\n".join(rows)


def _csv(team: Team) -> str:
    rows = ["player,salary,unlikely_incentives,years_remaining"]
    for c in team.contracts:
        rows.append(f"{c.player},{c.salary},{c.incentives_unlikely},{c.years_remaining}")
    return "\n".join(rows)


_FORMATS = (_markdown_table, _plain_columns, _csv)


def cap_sheet(team: Team, rng: random.Random | None = None, style: int | None = None) -> str:
    """Render a team's roster the way a cap sheet gets pasted into a chat."""
    if style is not None:
        render = _FORMATS[style % len(_FORMATS)]
    elif rng is not None:
        render = rng.choice(_FORMATS)
    else:
        render = _markdown_table

    header = [f"{team.name.upper()} -- {team.season} CAP SHEET", render(team)]

    footer = []
    if team.dead_money:
        footer.append(f"Dead money: {usd(team.dead_money)}")
    if team.cap_holds:
        footer.append(f"Cap holds: {usd(team.cap_holds)}")
    footer.append(f"Roster count: {team.roster_count}")
    if team.is_repeater:
        footer.append("Repeater taxpayer: yes")
    if team.hard_cap.value != "none":
        footer.append(f"Hard cap: {team.hard_cap.value}")
    if team.tpes_current_year:
        footer.append(
            "Traded player exceptions (this year): "
            + ", ".join(usd(t) for t in team.tpes_current_year)
        )
    if team.tpes_prior_year:
        footer.append(
            "Traded player exceptions (prior year): "
            + ", ".join(usd(t) for t in team.tpes_prior_year)
        )

    return "\n".join(header) + "\n\n" + "\n".join(footer)


def team_context(team: Team, rng: random.Random | None = None) -> str:
    """A constants block plus a cap sheet -- the standard preamble for a scenario prompt."""
    return f"{constants_block(team.constants)}\n\n{cap_sheet(team, rng=rng)}"
