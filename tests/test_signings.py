from capengine.constants import get_season
from capengine.models import HardCap
from capengine.signings import (
    ExceptionType,
    available_exceptions,
    can_sign_buyout_player,
    draft_penalties,
    evaluate_signing,
)
from tests.conftest import team_at

K = get_season("2026-27")


def status_for(team, exception: ExceptionType):
    return next(s for s in available_exceptions(team) if s.exception is exception)


# -- exception availability by tier ------------------------------------------------------


def test_over_the_tax_keeps_every_exception():
    """The tax line is financial; it costs money but takes nothing away."""
    team = team_at(205_000_000)
    assert status_for(team, ExceptionType.NON_TAXPAYER_MLE).available
    assert status_for(team, ExceptionType.TAXPAYER_MLE).available
    assert status_for(team, ExceptionType.BI_ANNUAL).available


def test_first_apron_loses_the_full_mid_level_and_bi_annual():
    team = team_at(215_000_000)
    assert not status_for(team, ExceptionType.NON_TAXPAYER_MLE).available
    assert not status_for(team, ExceptionType.BI_ANNUAL).available
    assert status_for(team, ExceptionType.TAXPAYER_MLE).available


def test_second_apron_loses_every_mid_level():
    team = team_at(230_000_000)
    assert not status_for(team, ExceptionType.NON_TAXPAYER_MLE).available
    assert not status_for(team, ExceptionType.TAXPAYER_MLE).available
    assert not status_for(team, ExceptionType.BI_ANNUAL).available
    assert status_for(team, ExceptionType.MINIMUM).available, "minimums always survive"


def test_room_exception_only_for_teams_with_cap_space():
    assert status_for(team_at(120_000_000), ExceptionType.ROOM).available
    assert not status_for(team_at(215_000_000), ExceptionType.ROOM).available


def test_room_exception_triggers_no_hard_cap():
    assert status_for(team_at(120_000_000), ExceptionType.ROOM).hard_cap_triggered is HardCap.NONE


# -- signings ------------------------------------------------------------------------------


def test_signing_within_the_mid_level_is_legal_and_hard_caps_the_team():
    team = team_at(190_000_000)
    result = evaluate_signing(team, 14_000_000, ExceptionType.NON_TAXPAYER_MLE)
    assert result.legal
    assert result.hard_cap_triggered is HardCap.FIRST_APRON


def test_signing_above_the_mid_level_amount_is_illegal():
    team = team_at(190_000_000)
    result = evaluate_signing(team, K.non_taxpayer_mle + 1_000_000, ExceptionType.NON_TAXPAYER_MLE)
    assert not result.legal
    assert any("exceeds" in r for r in result.reasons)


def test_mid_level_signing_that_would_breach_its_own_hard_cap_is_illegal():
    """Using the non-taxpayer mid-level caps you at the first apron -- including the signing."""
    team = team_at(200_000_000)
    result = evaluate_signing(team, 14_000_000, ExceptionType.NON_TAXPAYER_MLE)
    assert result.apron_salary_after == 214_000_000
    assert not result.legal
    assert any("hard cap" in r for r in result.reasons)


def test_second_apron_team_cannot_use_the_taxpayer_mid_level():
    team = team_at(230_000_000)
    result = evaluate_signing(team, 5_000_000, ExceptionType.TAXPAYER_MLE)
    assert not result.legal
    assert any("second apron" in r for r in result.reasons)


def test_full_roster_blocks_a_signing():
    team = team_at(190_000_000, roster=15)
    result = evaluate_signing(team, 5_000_000, ExceptionType.MINIMUM)
    assert not result.legal
    assert any("15 players" in r for r in result.reasons)


# -- buyout market ---------------------------------------------------------------------------


def test_buyout_ban_blocks_a_big_waivee_over_the_first_apron():
    team = team_at(215_000_000)
    result = can_sign_buyout_player(team, pre_waiver_salary=20_000_000)
    assert not result.allowed
    assert "non-taxpayer mid-level" in result.reason


def test_buyout_ban_permits_a_smaller_waivee():
    team = team_at(215_000_000)
    assert can_sign_buyout_player(team, pre_waiver_salary=10_000_000).allowed


def test_buyout_ban_does_not_apply_below_the_first_apron():
    team = team_at(190_000_000)
    assert can_sign_buyout_player(team, pre_waiver_salary=40_000_000).allowed


def test_buyout_threshold_is_the_non_taxpayer_mid_level_exactly():
    team = team_at(215_000_000)
    assert can_sign_buyout_player(team, K.non_taxpayer_mle).allowed
    assert not can_sign_buyout_player(team, K.non_taxpayer_mle + 1).allowed


# -- draft penalties ---------------------------------------------------------------------------


def test_second_apron_freezes_the_pick_seven_drafts_out():
    result = draft_penalties(team_at(230_000_000), current_draft_year=2026)
    assert result.pick_frozen
    assert result.frozen_draft_year == 2033
    assert not result.pick_demoted


def test_three_of_five_seasons_demotes_the_pick():
    result = draft_penalties(team_at(230_000_000), current_draft_year=2026, seasons_over_in_window=3)
    assert result.pick_demoted
    assert "end of the first round" in result.reason


def test_no_penalty_below_the_second_apron():
    result = draft_penalties(team_at(215_000_000), current_draft_year=2026)
    assert not result.pick_frozen
    assert result.frozen_draft_year is None
