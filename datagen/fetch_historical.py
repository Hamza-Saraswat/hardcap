"""Build historical cap sheets from an openly published dataset.

    python -m datagen.fetch_historical --seasons 2023-24 2024-25 2025-26

capsheets.com carries only the current league year, so past seasons come from
`Mr-Bridge/nba-salary-cap-contracts-2016-2026` on Hugging Face -- a compilation of
HoopsHype's public salary data (snapshot 2026-07-07), offered for research and educational
use with attribution to MrBridge (mr-bridge.com). Attribution travels with every record.

Scope is deliberately limited to the apron era. The 2023 CBA is what the model knows, and
loading a 2019-20 roster would invite it to apply apron rules that did not exist yet --
confidently and wrongly.

These sheets carry salaries only. Unlikely incentives, dead money, and cap holds are not in
the source, so historical payroll totals sit slightly below the official apron figures. The
picker states this rather than implying a precision the data does not have.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

from capengine.constants import SEASONS

DATASET = "Mr-Bridge/nba-salary-cap-contracts-2016-2026"
CSV_URL = f"https://huggingface.co/datasets/{DATASET}/raw/main/player_salaries.csv"
SOURCE_NAME = "MrBridge (mr-bridge.com) via HoopsHype, snapshot 2026-07-07"
USER_AGENT = "hardcap/0.1 (research project; +https://github.com/Hamza-Saraswat/hardcap)"

# 2024-25 onward only, and 2023-24's absence is deliberate rather than an oversight.
#
# 2023-24 was the 2023 CBA's transition year: a team over the first apron matched at 110% of
# outgoing salary, not the 100% that applies from 2024-25. The model never saw a 110%
# scenario in training, so handed a 2023-24 sheet it would apply 100% confidently and be
# wrong -- the precise failure this project is built to avoid. Adding the season would mean
# teaching the engine *and* retraining the model, not just fetching more rows.
#
# Its published thresholds are verified and on hand if that changes: cap $136,021,000,
# tax $165,294,000, first apron $172,346,000, second apron $182,794,000.
DEFAULT_SEASONS = ["2024-25", "2025-26"]

TEAM_ABBREV = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "LA Clippers": "LAC", "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM", "Miami Heat": "MIA", "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP", "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX", "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR", "Utah Jazz": "UTA",
    "Washington Wizards": "WAS",
}


def download() -> list[dict]:
    print(f"Downloading {DATASET} …")
    request = urllib.request.Request(CSV_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        text = response.read().decode("utf-8", errors="replace")
    rows = list(csv.DictReader(io.StringIO(text)))
    print(f"  {len(rows):,} salary rows across all seasons")
    return rows


def build(rows: list[dict], season: str) -> dict[str, dict]:
    """Group one season's salaries into per-team sheets."""
    by_team: dict[str, list[dict]] = defaultdict(list)
    skipped_teams: set[str] = set()

    for row in rows:
        if row.get("season") != season:
            continue
        if row.get("two_way", "").lower() == "true":
            continue  # two-way deals do not count against the cap the same way
        team = (row.get("team") or "").strip()
        abbrev = TEAM_ABBREV.get(team)
        if not abbrev:
            if team:
                skipped_teams.add(team)
            continue
        try:
            salary = int(float(row["salary"]))
        except (KeyError, TypeError, ValueError):
            continue
        if salary <= 0:
            continue
        by_team[abbrev].append({"name": row.get("player", "").strip(), "salary": salary})

    if skipped_teams:
        print(f"  note: unmapped team names ignored: {', '.join(sorted(skipped_teams))}")

    sheets = {}
    for abbrev, players in by_team.items():
        players.sort(key=lambda p: -p["salary"])
        sheets[abbrev] = {
            "team": next(n for n, a in TEAM_ABBREV.items() if a == abbrev),
            "abbrev": abbrev,
            "season": season,
            "players": players,
            "unlikely_incentives": {},
            "dead_money": 0,
            "total_payroll": sum(p["salary"] for p in players),
            "total_salaries": sum(p["salary"] for p in players),
            "apron_total": None,
            "first_apron_space": None,
            "second_apron_space": None,
            "luxury_tax_payment": None,
            "is_repeater": False,
            "hard_capped_at": None,
            "source": SOURCE_NAME,
            "source_url": f"https://huggingface.co/datasets/{DATASET}",
            "fetched": time.strftime("%Y-%m-%d"),
            "caveat": (
                "Salaries only -- unlikely incentives, dead money and cap holds are not in "
                "this source, so the payroll total runs below the official apron figure."
            ),
        }
    return sheets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seasons", nargs="*", default=DEFAULT_SEASONS)
    parser.add_argument("--out", type=Path, default=Path("data/capsheets"))
    args = parser.parse_args()

    unknown = [s for s in args.seasons if s not in SEASONS]
    if unknown:
        sys.exit(
            f"No cap thresholds on file for: {', '.join(unknown)}.\n"
            f"Available: {', '.join(sorted(SEASONS))}. Refusing to build a sheet the "
            "engine cannot reason about."
        )

    rows = download()
    for season in args.seasons:
        sheets = build(rows, season)
        if not sheets:
            print(f"{season}: no rows found -- skipping")
            continue
        out_dir = args.out / season
        out_dir.mkdir(parents=True, exist_ok=True)
        for abbrev, sheet in sorted(sheets.items()):
            (out_dir / f"{abbrev}.json").write_text(json.dumps(sheet, indent=2))
        counts = [len(s["players"]) for s in sheets.values()]
        print(f"{season}: {len(sheets)} teams -> {out_dir}  "
              f"(roster sizes {min(counts)}-{max(counts)})")


if __name__ == "__main__":
    main()
