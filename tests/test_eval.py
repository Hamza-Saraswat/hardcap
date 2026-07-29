"""Tests for eval scoring -- especially reading a verdict out of natural prose."""

from eval.harness import read_verdict, score_response, summarize


def test_reads_an_explicit_verdict_line():
    assert read_verdict("**Verdict: ILLEGAL.** The salary does not match.") == "ILLEGAL"
    assert read_verdict("**Verdict: LEGAL.** Everything checks out.") == "LEGAL"
    assert read_verdict("Verdict: NOT ALLOWED. He earned too much.") == "ILLEGAL"


def test_reads_a_verdict_stated_in_plain_language():
    assert read_verdict("No, that trade cannot be processed as constructed.") == "ILLEGAL"
    assert read_verdict("Yes, this works under the expanded bands.") == "LEGAL"


def test_a_legal_answer_may_still_discuss_what_would_be_illegal():
    """The common false negative: scanning the whole answer for the word 'illegal'."""
    response = (
        "**Verdict: LEGAL.** The matching works at 200% plus $250,000. Note that "
        "aggregating a second salary here would have been illegal over the second apron."
    )
    assert read_verdict(response) == "LEGAL"


def test_returns_none_when_no_verdict_is_stated():
    assert read_verdict("The team sits $4,500,000 below the second apron.") is None


def test_scoring_counts_required_figures_and_flags_inventions():
    row = {
        "kind": "trade_legality",
        "verdict": "ILLEGAL",
        "messages": [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "question"},
        ],
        "required_values": [14_827_471, 23_923_471],
        "allowed_values": [14_827_471, 23_923_471, 209_015_000],
    }
    response = (
        "**Verdict: ILLEGAL.** They send $14,827,471 and may absorb $23,923,471, "
        "but the return is $99,000,000."
    )
    score = score_response(row, response)

    assert score.verdict_correct is True
    assert score.required_hit == 2
    assert score.arithmetic_ok
    assert score.invented == [99_000_000]
    assert not score.grounded


def test_allowed_and_not_allowed_normalize_to_the_legal_axis():
    row = {
        "kind": "buyout_market",
        "verdict": "NOT ALLOWED",
        "messages": [{"role": "system", "content": ""}, {"role": "user", "content": ""}],
        "required_values": [],
        "allowed_values": [],
    }
    score = score_response(row, "**Verdict: NOT ALLOWED.** He was over the mid-level.")
    assert score.verdict_expected == "ILLEGAL"
    assert score.verdict_correct is True


def test_summary_separates_staleness_grounding():
    rows = []
    for kind, invented in (("anti_staleness", [1_000_000]), ("trade_legality", [])):
        row = {
            "kind": kind,
            "verdict": None,
            "messages": [{"role": "system", "content": ""}, {"role": "user", "content": ""}],
            "required_values": [],
            "allowed_values": [],
        }
        text = f"The figure is ${invented[0]:,}." if invented else "No figures here."
        rows.append(score_response(row, text))

    stats = summarize(rows)
    assert stats["grounding"] == 0.5
    assert stats["staleness_grounding"] == 0.0, "the staleness probe failed on its own terms"
