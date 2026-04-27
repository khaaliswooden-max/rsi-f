"""Eval harness for the wofo agent.

Two flavors of eval, both intentionally simple and dep-light:

- `signal`  — quantitative evals against a benchmark (info ratio,
  Jensen alpha, capture ratios, hit rate of "ADD" calls).
- `rubric`  — qualitative evals of research notes, scored either by an
  LLM judge (when an API key is configured) or by a deterministic
  heuristic when not.

`registry` orchestrates a suite of evals and writes a versioned report.
The report is the artifact the recursive-self-improvement loop reads to
decide whether a proposed change to wofo (prompt, tool, rule) is an
improvement or a regression.
"""
from .signal import (
    benchmark_compare,
    info_ratio,
    jensens_alpha,
    capture_ratios,
    factor_decompose,
    SignalEvalResult,
)
from .rubric import score_research_note, RubricResult, default_rubric
from .registry import EvalSuite, EvalCase, run_suite

__all__ = [
    "benchmark_compare",
    "info_ratio",
    "jensens_alpha",
    "capture_ratios",
    "factor_decompose",
    "SignalEvalResult",
    "score_research_note",
    "RubricResult",
    "default_rubric",
    "EvalSuite",
    "EvalCase",
    "run_suite",
]
