"""Default eval runner used by the RSI loop.

Defines `default_eval_runner(sandbox_root)` which runs a small,
deterministic eval suite — small enough that the loop can iterate
quickly, broad enough to catch regressions in the rubric heuristics
and the signal math.

The function takes a `sandbox_root` (str path) so it can be called
either against the live repo or against a sandbox copy. It does NOT
read any state from the caller's environment beyond `sandbox_root`.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path


# A handful of canned notes covering the spectrum from "obvious garbage"
# to "well-sourced research." A good rubric should score them in roughly
# this rank order.
CANNED_NOTES = [
    (
        "empty",
        "Hello.",
    ),
    (
        "vague",
        "I think tech stocks will go up next quarter. Buy NVDA.",
    ),
    (
        "moderate",
        "Situational Awareness LP added Bloom Energy in Q4 2025. "
        "BE is a fuel-cell maker — relevant to the AI-power thesis.",
    ),
    (
        "strong",
        "On 2026-02-11, Situational Awareness LP filed its 13F-HR "
        "(CIK 0002045724) for the period ending 2025-12-31, accession "
        "0002045724-26-000002. The fund reported $5.5 billion in long "
        "positions, with CoreWeave (CRWV) at 22.0% of the book. Bloom "
        "Energy (BE) is a new 16.5% position. Caveat: 13F is delayed by "
        "~45 days so this is backward-looking. Watchlist: monitor BE, "
        "CRWV, INTC across the next filing for conviction signals."
    ),
]


def default_eval_runner(sandbox_root: str | Path) -> dict:
    """Run the default eval suite against a sandbox repo and return the
    suite payload as a plain dict.

    Adds `sandbox_root` to sys.path for the duration of the call so
    that imported wofo modules come from the sandbox copy, not the
    live install.
    """
    import sys as _sys
    sandbox = str(sandbox_root)
    inserted = False
    if sandbox not in _sys.path:
        _sys.path.insert(0, sandbox)
        inserted = True
    try:
        # Force a fresh import of wofo from the sandbox path.
        for mod in list(_sys.modules):
            if mod == "wofo" or mod.startswith("wofo."):
                del _sys.modules[mod]

        from wofo.evals import EvalSuite, EvalCase, run_suite  # type: ignore

        cases: list = []
        for label, note in CANNED_NOTES:
            cases.append(EvalCase(name=f"rubric:{label}", kind="rubric", inputs={"note": note}))

        # Add a deterministic-but-noisy signal case using a seeded RNG so
        # info_ratio / Sharpe math is well-conditioned (zero-variance series
        # explode when divided by stdev).
        sd, sn, bd, bn = _seeded_paired_series(date(2024, 1, 1), 200)
        cases.append(EvalCase(
            name="signal:outperform_synthetic",
            kind="signal",
            inputs={"s_dates": sd, "s_nav": sn, "b_dates": bd, "b_nav": bn},
        ))

        suite = EvalSuite(name="rsi_default", cases=cases)
        # Redirect run-output dir into the sandbox so we don't pollute the live
        # wofo/data/evals tree on every loop iteration.
        import wofo.evals.registry as _reg
        _reg.RUNS_DIR = Path(sandbox) / "wofo" / "data" / "evals" / "runs"
        return run_suite(suite, label="rsi")
    finally:
        if inserted:
            try:
                _sys.path.remove(sandbox)
            except ValueError:
                pass


def _seeded_paired_series(start: date, n: int):
    """Return (s_dates, s_nav, b_dates, b_nav) for a strategy that beats its
    benchmark by ~2 bps/day with shared market noise.

    Deterministic (seeded) so the eval is reproducible across runs.
    """
    import random as _r
    rng = _r.Random("wofo-rsi-default-eval")
    s_nav: list = [100.0]
    b_nav: list = [100.0]
    dates: list = []
    cur = start
    while len(dates) < n:
        if cur.weekday() < 5:
            dates.append(cur)
            mkt = rng.gauss(0.0005, 0.012)
            edge = rng.gauss(0.0002, 0.002)
            s_nav.append(s_nav[-1] * (1 + mkt + edge))
            b_nav.append(b_nav[-1] * (1 + mkt))
        cur += timedelta(days=1)
    return dates, s_nav[: len(dates)], dates, b_nav[: len(dates)]
