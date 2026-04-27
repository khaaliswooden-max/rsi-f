"""Compare baseline vs proposed eval payloads and emit a verdict.

Inputs are the dicts returned by `wofo.evals.registry.run_suite`. We
compare on the suite's `summary` block, which is averaged over cases.
For now, the judge uses a simple threshold rule:

- IMPROVE       — proposed > baseline by `min_delta` AND no metric
                  regressed by more than `max_regression`.
- REGRESS       — proposed < baseline by `min_delta` on the primary
                  metric.
- INCONCLUSIVE  — change is within the threshold, OR a sub-metric
                  improved while another regressed.

This is intentionally simple. A more sophisticated judge could use
bootstrap CIs on the rubric scores or t-tests on signal alphas; that
belongs in a v2 once we have enough proposal outcomes to calibrate
thresholds.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Verdict:
    label: str          # IMPROVE / REGRESS / INCONCLUSIVE
    primary_metric: str
    baseline: float
    proposed: float
    delta: float
    rationale: str


# Map from suite summary key -> "higher is better"
HIGHER_IS_BETTER = {
    "rubric_mean_fraction": True,
    "signal_mean_alpha_annual": True,
    "signal_mean_info_ratio": True,
}


def judge_outcome(
    baseline: dict,
    proposed: dict,
    *,
    primary_metric: str = "rubric_mean_fraction",
    min_delta: float = 0.02,
    max_regression: float = 0.03,
) -> Verdict:
    """Classify (baseline, proposed) eval payloads."""
    bsum = (baseline or {}).get("summary", {})
    psum = (proposed or {}).get("summary", {})
    if primary_metric not in bsum or primary_metric not in psum:
        return Verdict(
            label="INCONCLUSIVE",
            primary_metric=primary_metric,
            baseline=float("nan"),
            proposed=float("nan"),
            delta=float("nan"),
            rationale=f"primary metric {primary_metric} not in both payloads",
        )
    b = float(bsum[primary_metric])
    p = float(psum[primary_metric])
    delta = p - b if HIGHER_IS_BETTER.get(primary_metric, True) else b - p

    # Check for regressions in any other tracked metric.
    regressions: list[str] = []
    for k, higher in HIGHER_IS_BETTER.items():
        if k == primary_metric:
            continue
        if k not in bsum or k not in psum:
            continue
        bk = float(bsum[k])
        pk = float(psum[k])
        sub_delta = (pk - bk) if higher else (bk - pk)
        if sub_delta < -max_regression:
            regressions.append(f"{k}: {bk:.3f} -> {pk:.3f} ({sub_delta:+.3f})")

    if delta >= min_delta and not regressions:
        return Verdict(
            label="IMPROVE",
            primary_metric=primary_metric,
            baseline=b, proposed=p, delta=delta,
            rationale=f"{primary_metric} +{delta:.3f}; no metric regressed > {max_regression}",
        )
    if delta <= -min_delta:
        return Verdict(
            label="REGRESS",
            primary_metric=primary_metric,
            baseline=b, proposed=p, delta=delta,
            rationale=f"{primary_metric} {delta:+.3f}",
        )
    if regressions:
        return Verdict(
            label="INCONCLUSIVE",
            primary_metric=primary_metric,
            baseline=b, proposed=p, delta=delta,
            rationale=f"primary {delta:+.3f} but regressions in: " + "; ".join(regressions),
        )
    return Verdict(
        label="INCONCLUSIVE",
        primary_metric=primary_metric,
        baseline=b, proposed=p, delta=delta,
        rationale=f"|delta| {abs(delta):.3f} below min_delta {min_delta}",
    )
