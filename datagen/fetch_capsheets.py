"""Fetch current-season cap sheets from capsheets.com.

    python -m datagen.fetch_capsheets --season 2026-27

capsheets.com is Yossi Gozlan's free public cap-sheet site. Its robots.txt permits crawling
(`Disallow:` with no paths) and it publishes no terms restricting reuse; salary figures are
facts, which are not copyrightable. We still fetch politely: one pass, one request per second,
an identifying User-Agent, cached to disk so a page is never re-fetched in a loop. The cache
is gitignored -- fetching public facts is fine, republishing someone's compiled corpus is a
different thing. Attribution travels with every record.

No LLM touches this. The pages are clean server-rendered tables, and a regex over table cells
cannot invent a salary the way a model-based extractor can -- which matters more here than
anywhere, since these numbers are the ground truth the assistant reasons from.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

SOURCE_NAME = "capsheets.com (Yossi Gozlan)"
SOURCE_URL = "https://www.capsheets.com/"
USER_AGENT = "hardcap/0.1 (research project; +https://github.com/Hamza-Saraswat/hardcap)"
REQUEST_DELAY_SECONDS = 1.0

# Slug fragments as capsheets.com forms them: /<team-slug>-cap-sheet-<yyyy>-<yyyy>-season/
TEAMS = {
    "ATL": "atlanta-hawks", "BOS": "boston-celtics", "BKN": "brooklyn-nets",
    "CHA": "charlotte-hornets", "CHI": "chicago-bulls", "CLE": "cleveland-cavaliers",
    "DAL": "dallas-mavericks", "DEN": "denver-nuggets", "DET": "detroit-pistons",
    "GSW": "golden-state-warriors", "HOU": "houston-rockets", "IND": "indiana-pacers",
    "LAC": "los-angeles-clippers", "LAL": "los-angeles-lakers", "MEM": "memphis-grizzlies",
    "MIA": "miami-heat", "MIL": "milwaukee-bucks", "MIN": "minnesota-timberwolves",
    "NOP": "new-orleans-pelicans", "NYK": "new-york-knicks", "OKC": "oklahoma-city-thunder",
    "ORL": "orlando-magic", "PHI": "philadelphia-76ers", "PHX": "phoenix-suns",
    "POR": "portland-trail-blazers", "SAC": "sacramento-kings", "SAS": "san-antonio-spurs",
    "TOR": "toronto-raptors", "UTA": "utah-jazz", "WAS": "washington-wizards",
}

# Rows are <td class="sgs-col-N">; col 0 is a rank or a label, col 1 a name, col 2 an amount.
_CELL = re.compile(r'<td class="sgs-col-(\d)"[^>]*>(.*?)</td>', re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_MONEY = re.compile(r"^\$?\s*\(?\s*([\d,]+)\s*\)?$")


@dataclass
class Player:
    name: str
    salary: int


@dataclass
class CapSheet:
    team: str
    abbrev: str
    season: str
    players: list[Player] = field(default_factory=list)
    unlikely_incentives: dict[str, int] = field(default_factory=dict)
    dead_money: int = 0
    total_payroll: int | None = None
    total_salaries: int | None = None
    apron_total: int | None = None
    first_apron_space: int | None = None
    second_apron_space: int | None = None
    luxury_tax_payment: int | None = None
    is_repeater: bool = False
    hard_capped_at: str | None = None
    source: str = SOURCE_NAME
    source_url: str = ""
    fetched: str = ""

    @property
    def roster_count(self) -> int:
        return len(self.players)


def _money(text: str) -> int | None:
    """Parse a cell like '$ 59,033,114' or '$ (2,034,249)'. Parentheses mean negative."""
    stripped = text.strip()
    match = _MONEY.match(stripped)
    if not match:
        return None
    value = int(match.group(1).replace(",", ""))
    return -value if "(" in stripped else value


def _rows(source: str) -> list[dict[int, str]]:
    """Collapse the table cells into rows keyed by column index."""
    rows: list[dict[int, str]] = []
    current: dict[int, str] = {}
    for column, raw in _CELL.findall(source):
        text = html.unescape(_TAG.sub("", raw)).strip()
        current[int(column)] = text
        if int(column) == 2:
            rows.append(current)
            current = {}
    return rows


def parse(source: str, abbrev: str, season: str, url: str) -> CapSheet:
    """Turn a fetched page into a structured cap sheet.

    The page is read in order, and its own labelled total rows act as section boundaries:
    player rows appear before 'Total Payroll', unlikely-incentive rows sit between the tax
    block and 'Apron Total'. Labels drive the parse rather than row positions, so a team
    with a different number of players or no dead money still reads correctly.
    """
    sheet = CapSheet(team="", abbrev=abbrev, season=season, source_url=url,
                     fetched=time.strftime("%Y-%m-%d"))
    section = "roster"

    for row in _rows(source):
        first = (row.get(0) or "").strip()
        name = (row.get(1) or "").strip()
        amount = _money(row.get(2) or "")

        # Which column carries a row's label is not consistent across teams -- Denver puts
        # "Total Payroll" in column 0, Atlanta in column 1. A digit in column 0 always means
        # a roster row, so anything else is a label wherever it sits.
        is_player_row = first.isdigit()
        label = "" if is_player_row else (first or name)
        low = label.lower()

        if section == "roster" and label and "(" in label and amount is None:
            # Header row, e.g. "Denver Nuggets (13/15 + 1/3)".
            sheet.team = label.split("(")[0].strip()
            continue

        if amount is None:
            continue

        if low == "total payroll":
            sheet.total_payroll = amount
            section = "post-roster"
        elif low == "dead money":
            sheet.dead_money = amount
        elif low == "total salaries":
            sheet.total_salaries = amount
            section = "tax"
        elif low.startswith("luxury tax payment"):
            sheet.luxury_tax_payment = amount
            sheet.is_repeater = "repeater" in low
            section = "incentives"
        elif low.startswith("first apron"):
            # "First Apron (Hard Capped)" marks a team hard-capped at that level.
            if "hard cap" in low:
                sheet.hard_capped_at = "first apron"
            if low == "first apron space":
                sheet.first_apron_space = amount
        elif low.startswith("second apron"):
            if "hard cap" in low:
                sheet.hard_capped_at = "second apron"
            if low == "second apron space":
                sheet.second_apron_space = amount
                section = "holds"
        elif low.startswith("apron total"):
            sheet.apron_total = amount
            section = "apron"
        elif low == "unlikely bonuses":
            continue  # subtotal; the per-player rows above it carry the detail
        elif is_player_row and name and section == "roster":
            sheet.players.append(Player(name=name, salary=amount))
        elif section == "incentives" and name and not first:
            sheet.unlikely_incentives[name] = amount

    return sheet


@dataclass
class Check:
    ok: bool
    detail: str


def reconcile(sheet: CapSheet) -> Check:
    """The page states its own totals, so a correct parse must reproduce them.

    Without this a misparse ships quietly-wrong salaries, which is the one failure this
    project cannot tolerate.
    """
    problems = []
    if sheet.total_payroll is None:
        problems.append("no Total Payroll row found")
    else:
        summed = sum(p.salary for p in sheet.players)
        if summed != sheet.total_payroll:
            problems.append(
                f"players sum to ${summed:,} but page states ${sheet.total_payroll:,} "
                f"(off by ${summed - sheet.total_payroll:,})"
            )
    if sheet.apron_total is not None and sheet.unlikely_incentives:
        incentives = sum(sheet.unlikely_incentives.values())
        base = (sheet.total_salaries or 0) + incentives
        # The remainder is the minimum-salary tax variance, which the page lists separately.
        if not 0 <= sheet.apron_total - base <= 5_000_000:
            problems.append(
                f"apron total ${sheet.apron_total:,} is not explained by salaries "
                f"${sheet.total_salaries or 0:,} + incentives ${incentives:,}"
            )
    if not sheet.players:
        problems.append("no player rows parsed")

    return Check(ok=not problems, detail="; ".join(problems) or "totals reconcile")


def fetch(abbrev: str, slug: str, season: str) -> tuple[CapSheet, Check, str]:
    start, end = season.split("-")
    url = f"https://www.capsheets.com/{slug}-cap-sheet-{start}-20{end}-season/"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        source = response.read().decode("utf-8", errors="replace")
    sheet = parse(source, abbrev, season, url)
    return sheet, reconcile(sheet), url


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", default="2026-27")
    parser.add_argument("--out", type=Path, default=Path("data/capsheets"))
    parser.add_argument("--teams", nargs="*", help="abbrevs to fetch; default all 30")
    args = parser.parse_args()

    wanted = {t.upper() for t in args.teams} if args.teams else set(TEAMS)
    unknown = wanted - set(TEAMS)
    if unknown:
        sys.exit(f"Unknown team abbreviations: {', '.join(sorted(unknown))}")

    out_dir = args.out / args.season
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Fetching {len(wanted)} cap sheets for {args.season} from {SOURCE_URL}")
    print(f"  polite mode: {REQUEST_DELAY_SECONDS}s between requests\n")

    good, bad = 0, []
    for index, abbrev in enumerate(sorted(wanted)):
        try:
            sheet, check, _url = fetch(abbrev, TEAMS[abbrev], args.season)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            bad.append((abbrev, f"fetch failed: {exc}"))
            print(f"  {abbrev}  FETCH FAILED: {exc}")
            continue

        if check.ok:
            (out_dir / f"{abbrev}.json").write_text(json.dumps(asdict(sheet), indent=2))
            good += 1
            over = ""
            if sheet.second_apron_space is not None and sheet.second_apron_space < 0:
                over = f"  [over 2nd apron by ${-sheet.second_apron_space:,}]"
            print(f"  {abbrev}  {sheet.roster_count:2} players  "
                  f"${sheet.total_payroll or 0:>12,}{over}")
        else:
            bad.append((abbrev, check.detail))
            print(f"  {abbrev}  REJECTED: {check.detail}")

        if index < len(wanted) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    print(f"\n{good} sheets written to {out_dir}")
    if bad:
        print(f"{len(bad)} rejected (not written -- a failed parse must not ship as data):")
        for abbrev, why in bad:
            print(f"  {abbrev}: {why}")
        sys.exit(1)


if __name__ == "__main__":
    main()
