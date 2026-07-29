"""CapEngine -- a deterministic NBA salary cap calculator for the 2023 CBA.

This is the ground-truth layer of the project. It never guesses: every figure it reports is
either a published constant or arithmetic performed on one, and every result carries a
`Trace` recording each step so generated training prose can be verified number by number.

Scope: the 2023 CBA as it stands for the 2024-25 through 2026-27 league years.
"""

from capengine.constants import SEASONS, SeasonConstants, get_season
from capengine.models import ApronLevel, Contract, HardCap, OptionType, Team
from capengine.signings import (
    ExceptionType,
    available_exceptions,
    can_sign_buyout_player,
    compute_stretch,
    draft_penalties,
    evaluate_signing,
)
from capengine.tax import compute_tax
from capengine.trace import Trace, usd
from capengine.trade import TradeSide, evaluate_trade, max_incoming_expanded

__all__ = [
    "SEASONS",
    "ApronLevel",
    "Contract",
    "ExceptionType",
    "HardCap",
    "OptionType",
    "SeasonConstants",
    "Team",
    "Trace",
    "TradeSide",
    "available_exceptions",
    "can_sign_buyout_player",
    "compute_stretch",
    "compute_tax",
    "draft_penalties",
    "evaluate_signing",
    "evaluate_trade",
    "get_season",
    "max_incoming_expanded",
    "usd",
]
