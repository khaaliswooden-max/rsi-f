"""Tests for signal + rubric evals."""
from datetime import date, timedelta

from wofo.evals import (
    benchmark_compare,
    info_ratio,
    jensens_alpha,
    capture_ratios,
    score_research_note,
    EvalSuite,
    EvalCase,
    run_suite,
)


def _series(start: date, n: int, daily_ret: float, start_nav: float = 100.0) -> tuple[list[date], list[float]]:
    dates, nav = [], []
    cur = start
    val = start_nav
    while len(dates) < n:
        if cur.weekday() < 5:
            dates.append(cur)
            nav.append(val)
            val *= 1 + daily_ret
        cur += timedelta(days=1)
    return dates, nav


def test_perfect_correlation_yields_beta_one_zero_alpha():
    d, b_nav = _series(date(2024, 1, 1), 200, 0.001)
    s_nav = list(b_nav)  # identical
    j = jensens_alpha(d, s_nav, d, b_nav)
    assert abs(j["beta"] - 1.0) < 1e-6
    assert abs(j["alpha_annual"]) < 1e-6
    assert j["r_squared"] > 0.999


def test_strategy_2x_benchmark_returns_beta_two():
    # Deterministic series have zero variance -> regression is degenerate.
    # Use a noisy benchmark and apply a 2x leverage to it.
    import random
    rng = random.Random(42)
    b_nav = [100.0]
    for _ in range(199):
        b_nav.append(b_nav[-1] * (1 + rng.gauss(0.0005, 0.01)))
    s_nav = [100.0]
    for i in range(1, len(b_nav)):
        s_nav.append(s_nav[-1] * (1 + 2 * (b_nav[i] / b_nav[i - 1] - 1)))
    d = [date(2024, 1, 1) + timedelta(days=i) for i in range(len(b_nav))]
    j = jensens_alpha(d, s_nav, d, b_nav)
    assert abs(j["beta"] - 2.0) < 0.01
    assert j["r_squared"] > 0.99


def test_info_ratio_zero_for_identical_series():
    d, n = _series(date(2024, 1, 1), 200, 0.001)
    assert abs(info_ratio(d, n, d, n)) < 1e-9


def test_capture_ratios_expected_signs():
    d, b_nav = _series(date(2024, 1, 1), 200, 0.001)
    s_dates, s_nav = _series(date(2024, 1, 1), 200, 0.0015)  # consistently better
    cap = capture_ratios(s_dates, s_nav, d, b_nav)
    assert cap["up_capture"] > 1.0   # outperforms in up markets
    assert cap["down_capture"] < 1.0 or cap["down_capture"] == 0.0


def test_benchmark_compare_smoke():
    d, b_nav = _series(date(2024, 1, 1), 200, 0.001)
    s_dates, s_nav = _series(date(2024, 1, 1), 200, 0.0012)
    r = benchmark_compare(s_dates, s_nav, d, b_nav)
    assert r.n_days >= 100
    assert r.cagr_strategy > r.cagr_benchmark


def test_rubric_heuristic_high_for_strong_note():
    note = (
        "On 2026-02-11, Situational Awareness LP filed its 13F-HR (CIK 0002045724) "
        "covering the period 2025-12-31. The accession 0002045724-26-000002 reports "
        "$5.5 billion in long positions. CoreWeave (CRWV) is 22.0% of the book. "
        "Note: 13F is delayed 45 days so this is backward-looking. Watchlist: "
        "monitor BE, CRWV, and INTC. We expect the manager to maintain conviction next quarter."
    )
    r = score_research_note(note, use_llm=False)
    # Should hit most criteria. Don't pin to exact score (heuristic is fuzzy).
    assert r.total >= 13   # of 18 max
    assert r.judge == "heuristic"


def test_rubric_heuristic_low_for_empty_note():
    r = score_research_note("nothing to see here", use_llm=False)
    assert r.total <= 6


def test_run_suite_writes_artifacts(tmp_path, monkeypatch):
    # Redirect runs dir into the tmp dir to avoid polluting the repo.
    import wofo.evals.registry as reg
    monkeypatch.setattr(reg, "RUNS_DIR", tmp_path)

    d, b = _series(date(2024, 1, 1), 100, 0.001)
    sd, sn = _series(date(2024, 1, 1), 100, 0.0012)
    suite = EvalSuite(
        name="test_suite",
        cases=[
            EvalCase("rubric_strong",
                     "rubric",
                     {"note": "13F filed 2026-02-11, accession 0002045724-26-000002, $5B AUM, 22.0%, watchlist."}),
            EvalCase("signal_outperformance",
                     "signal",
                     {"s_dates": sd, "s_nav": sn, "b_dates": d, "b_nav": b}),
        ],
    )
    payload = run_suite(suite, label="t")
    assert (tmp_path / payload["__path"].split("/")[-1] / "result.json").exists() or any(p.is_dir() for p in tmp_path.iterdir())
    assert payload["summary"]["rubric_n"] == 1
    assert payload["summary"]["signal_n"] == 1
