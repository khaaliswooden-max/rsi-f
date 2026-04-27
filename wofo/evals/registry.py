"""Eval suite + versioned report writer.

A `RecordedRun` is the artifact the recursive-self-improvement loop
reads. Two runs of the same suite at different code versions can be
compared to decide whether a proposed change is an improvement.

Run layout:
    wofo/data/evals/runs/{ts}_{label}/
        result.json   — full result payload
        result.md     — human-readable summary
        suite.json    — copy of the suite definition that was run
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .rubric import RubricResult, default_rubric, score_research_note
from .signal import SignalEvalResult


REPO = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO / "wofo" / "data" / "evals" / "runs"


@dataclass
class EvalCase:
    """One eval case in a suite.

    A case bundles a `kind` (signal | rubric) with the inputs needed to
    produce a result. Suites can mix kinds.
    """

    name: str
    kind: str
    inputs: dict[str, Any]


@dataclass
class EvalSuite:
    name: str
    cases: list[EvalCase] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "cases": [{"name": c.name, "kind": c.kind, "inputs": _public_inputs(c.inputs)} for c in self.cases],
        }


def _public_inputs(d: dict) -> dict:
    """Strip non-serializable / sensitive fields before recording inputs."""
    out: dict = {}
    for k, v in d.items():
        if callable(v):
            out[k] = "<callable>"
        elif k.endswith("_dates") or k.endswith("_nav"):
            out[k] = f"<series len={len(v)}>"
        elif k == "note":
            out[k] = v[:200] + ("..." if len(v) > 200 else "")
        else:
            try:
                json.dumps(v)
                out[k] = v
            except TypeError:
                out[k] = repr(v)[:200]
    return out


def _git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO), stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return None


def run_suite(suite: EvalSuite, label: str = "run") -> dict:
    """Run all cases and write artifacts to disk.

    Returns the in-memory result dict; the canonical record is on disk.
    """
    results: list[dict] = []
    for case in suite.cases:
        results.append({"name": case.name, "kind": case.kind, "result": _run_case(case)})

    payload = {
        "suite": suite.name,
        "label": label,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": _git_sha(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "results": results,
        "summary": _summarize(results),
    }

    ts_safe = payload["timestamp_utc"].replace(":", "").replace("-", "")
    out = RUNS_DIR / f"{ts_safe}_{_safe(label)}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(payload, indent=2, default=str))
    (out / "suite.json").write_text(json.dumps(suite.to_dict(), indent=2, default=str))
    (out / "result.md").write_text(_format_md(payload))
    payload["__path"] = str(out)
    return payload


def _run_case(case: EvalCase) -> dict:
    kind = case.kind
    if kind == "rubric":
        note = case.inputs["note"]
        criteria = case.inputs.get("criteria") or default_rubric()
        result: RubricResult = score_research_note(note, criteria=criteria)
        return {
            "judge": result.judge,
            "criteria_scores": result.criteria_scores,
            "rationales": result.rationales,
            "total": result.total,
            "max_total": result.max_total,
            "score_fraction": result.total / result.max_total if result.max_total else 0.0,
        }
    if kind == "signal":
        from .signal import benchmark_compare
        r: SignalEvalResult = benchmark_compare(
            case.inputs["s_dates"], case.inputs["s_nav"],
            case.inputs["b_dates"], case.inputs["b_nav"],
        )
        return r.to_dict()
    raise ValueError(f"unknown eval kind: {kind}")


def _summarize(results: list[dict]) -> dict:
    rubric_results = [r["result"] for r in results if r["kind"] == "rubric"]
    signal_results = [r["result"] for r in results if r["kind"] == "signal"]
    summary: dict = {}
    if rubric_results:
        scores = [r["score_fraction"] for r in rubric_results]
        summary["rubric_mean_fraction"] = sum(scores) / len(scores)
        summary["rubric_n"] = len(rubric_results)
    if signal_results:
        summary["signal_mean_alpha_annual"] = sum(r["alpha_annual"] for r in signal_results) / len(signal_results)
        summary["signal_mean_info_ratio"] = sum(r["info_ratio"] for r in signal_results) / len(signal_results)
        summary["signal_n"] = len(signal_results)
    return summary


def _format_md(payload: dict) -> str:
    lines = [
        f"# Eval run — {payload['suite']} ({payload['label']})",
        "",
        f"- Timestamp: {payload['timestamp_utc']}",
        f"- Git SHA: `{payload['git_sha'] or 'n/a'}`",
        f"- Python: {payload['python']}",
        "",
        "## Summary",
        "",
    ]
    for k, v in payload["summary"].items():
        lines.append(f"- **{k}**: {v if isinstance(v, int) else f'{v:.4f}'}")
    lines += ["", "## Cases", ""]
    for r in payload["results"]:
        lines.append(f"### {r['name']} ({r['kind']})")
        lines.append("")
        for k, v in r["result"].items():
            if k == "rationales":
                continue
            if isinstance(v, float):
                lines.append(f"- {k}: {v:.4f}")
            else:
                lines.append(f"- {k}: {v}")
        lines.append("")
    return "\n".join(lines) + "\n"


def _safe(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in s)
