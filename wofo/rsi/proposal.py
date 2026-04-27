"""Proposal data structures."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


@dataclass
class Proposal:
    """A single, narrow change to a wofo source file.

    `target_path` is repo-relative (e.g. "wofo/evals/rubric.py").
    `new_content` is the *full* new file body. We don't store unified
    diffs because applying a full file is simpler and removes a class
    of "diff didn't apply cleanly" failure modes.
    """
    label: str
    target_path: str
    new_content: str
    rationale: str
    proposer: str = "unknown"
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


@dataclass
class ProposalOutcome:
    """The recorded outcome of evaluating a proposal."""
    proposal: Proposal
    baseline_eval: dict          # full eval-suite payload, baseline run
    proposed_eval: dict          # full eval-suite payload, proposed run
    delta: dict                  # judge_outcome() output
    verdict: str                 # IMPROVE | REGRESS | INCONCLUSIVE | ERROR
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "proposal": asdict(self.proposal),
            "baseline_eval": self.baseline_eval,
            "proposed_eval": self.proposed_eval,
            "delta": self.delta,
            "verdict": self.verdict,
            "error": self.error,
        }
