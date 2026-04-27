"""Tests for the RSI loop.

We test the judge directly with synthetic eval payloads so we don't
have to spin up a sandbox in unit tests. The full sandbox path is
exercised in `wofo.rsi.cli demo`.
"""
from wofo.rsi import judge_outcome, MockProposer, Proposal
from wofo.rsi.judge import Verdict


def _payload(rubric=0.5, alpha=0.0, info=0.0):
    return {"summary": {
        "rubric_mean_fraction": rubric,
        "signal_mean_alpha_annual": alpha,
        "signal_mean_info_ratio": info,
    }}


def test_judge_improve():
    v = judge_outcome(_payload(rubric=0.50), _payload(rubric=0.65))
    assert v.label == "IMPROVE"
    assert v.delta > 0


def test_judge_regress():
    v = judge_outcome(_payload(rubric=0.60), _payload(rubric=0.40))
    assert v.label == "REGRESS"
    assert v.delta < 0


def test_judge_inconclusive_within_threshold():
    v = judge_outcome(_payload(rubric=0.50), _payload(rubric=0.51))
    assert v.label == "INCONCLUSIVE"


def test_judge_inconclusive_when_other_metric_regresses():
    v = judge_outcome(
        _payload(rubric=0.50, alpha=0.10),
        _payload(rubric=0.55, alpha=0.05),  # rubric up but alpha down 5pp > 3pp tol
    )
    assert v.label == "INCONCLUSIVE"
    assert "regression" in v.rationale.lower() or "regress" in v.rationale.lower()


def test_mock_proposer_yields_in_order():
    proposals = [
        Proposal(label="a", target_path="x.py", new_content="A", rationale="", proposer="t"),
        Proposal(label="b", target_path="x.py", new_content="B", rationale="", proposer="t"),
    ]
    mp = MockProposer(proposals)
    got = list(mp.propose())
    assert [p.label for p in got] == ["a", "b"]


def test_judge_handles_missing_metric():
    v = judge_outcome({"summary": {}}, {"summary": {}})
    assert v.label == "INCONCLUSIVE"
    assert "not in both" in v.rationale
