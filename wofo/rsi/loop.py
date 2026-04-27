"""Recursive self-improvement loop orchestrator.

Pseudo-code:
    baseline = run_eval()                # against current code
    for proposal in proposer:
        result = run_in_sandbox(proposal, run_eval)
        verdict = judge(baseline, result.eval_payload)
        record(proposal, baseline, result, verdict)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .judge import judge_outcome, Verdict
from .proposal import Proposal, ProposalOutcome
from .proposers import Proposer
from .sandbox import run_in_sandbox


REPO = Path(__file__).resolve().parents[2]
RSI_DIR = REPO / "wofo" / "data" / "rsi"


@dataclass
class LoopReport:
    started_utc: str
    finished_utc: str
    baseline: dict
    outcomes: list[ProposalOutcome] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "started_utc": self.started_utc,
            "finished_utc": self.finished_utc,
            "baseline": self.baseline,
            "outcomes": [o.to_dict() for o in self.outcomes],
        }


def run_loop(
    proposer: Proposer,
    eval_runner: Callable[[Path], dict],
    *,
    primary_metric: str = "rubric_mean_fraction",
    min_delta: float = 0.02,
    max_regression: float = 0.03,
    label: str = "rsi",
) -> LoopReport:
    """Run the full loop. Returns a `LoopReport` and writes artifacts."""
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # Baseline is the current code (no proposal applied) — eval against the live tree.
    baseline = eval_runner(REPO)
    outcomes: list[ProposalOutcome] = []

    for prop in proposer.propose():
        sb = run_in_sandbox(prop, eval_runner)
        if sb.error or sb.eval_payload is None:
            outcomes.append(ProposalOutcome(
                proposal=prop, baseline_eval=baseline, proposed_eval={},
                delta={}, verdict="ERROR", error=sb.error or "no eval payload",
            ))
            continue
        v: Verdict = judge_outcome(
            baseline, sb.eval_payload,
            primary_metric=primary_metric,
            min_delta=min_delta,
            max_regression=max_regression,
        )
        outcomes.append(ProposalOutcome(
            proposal=prop, baseline_eval=baseline, proposed_eval=sb.eval_payload,
            delta={
                "primary_metric": v.primary_metric,
                "baseline": v.baseline, "proposed": v.proposed, "delta": v.delta,
                "rationale": v.rationale,
            },
            verdict=v.label,
        ))

    finished = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report = LoopReport(started_utc=started, finished_utc=finished, baseline=baseline, outcomes=outcomes)

    out_dir = RSI_DIR / "runs" / f"{started.replace(':','').replace('-','')}_{_safe(label)}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report.to_dict(), indent=2, default=str))
    (out_dir / "report.md").write_text(_format_md(report))
    return report


def _safe(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in s)


def _format_md(r: LoopReport) -> str:
    lines = [
        "# RSI loop report",
        "",
        f"- Started:  {r.started_utc}",
        f"- Finished: {r.finished_utc}",
        f"- Baseline summary: `{r.baseline.get('summary', {})}`",
        "",
        "## Proposals",
        "",
    ]
    for o in r.outcomes:
        p = o.proposal
        d = o.delta
        lines.append(f"### {p.label} → **{o.verdict}**")
        lines.append("")
        lines.append(f"- Target: `{p.target_path}`")
        lines.append(f"- Proposer: `{p.proposer}`")
        lines.append(f"- Rationale: {p.rationale}")
        if d:
            lines.append(
                f"- {d['primary_metric']}: {d['baseline']:.4f} → "
                f"{d['proposed']:.4f} (Δ {d['delta']:+.4f})"
            )
            lines.append(f"- Judge: {d['rationale']}")
        if o.error:
            lines.append(f"- Error: `{o.error}`")
        lines.append("")
    lines += [
        "## Disposition",
        "",
        "Proposals labeled **IMPROVE** are candidates for human review and",
        "merge. **REGRESS** and **INCONCLUSIVE** proposals should not be",
        "merged but are kept on disk for failure analysis. **ERROR** proposals",
        "indicate sandbox-execution problems and should be reproduced manually.",
    ]
    return "\n".join(lines) + "\n"
