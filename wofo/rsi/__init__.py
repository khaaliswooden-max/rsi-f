"""Recursive self-improvement loop.

The wofo agent proposes changes to its own code (prompts, tools,
heuristics, rules), and this module evaluates each proposal against an
eval suite in an isolated sandbox to decide whether the change is an
improvement.

Crucially: this is **not** an autonomous deployment loop. The output
of `run_loop()` is an artifact on disk that a human reviews and
decides whether to merge. We never commit to `main` from the loop, we
never run untrusted code outside the sandbox, and we never accept a
proposal whose eval delta is statistically inconclusive.

Modules:
- `proposal`  — `Proposal` dataclass.
- `proposers` — pluggable proposal generators (mock, file, LLM).
- `sandbox`   — apply a proposal to a tmp copy of the repo, run evals.
- `judge`     — classify a proposal as IMPROVE / REGRESS / INCONCLUSIVE.
- `loop`      — orchestrate baseline → propose → sandbox → judge → record.
- `cli`       — `python -m wofo.rsi.cli`.
"""
from .proposal import Proposal, ProposalOutcome
from .proposers import Proposer, MockProposer, FileProposer
from .sandbox import run_in_sandbox, SandboxResult
from .judge import judge_outcome, Verdict
from .loop import run_loop, LoopReport
from .eval_runner import default_eval_runner

__all__ = [
    "Proposal",
    "ProposalOutcome",
    "Proposer",
    "MockProposer",
    "FileProposer",
    "run_in_sandbox",
    "SandboxResult",
    "judge_outcome",
    "Verdict",
    "run_loop",
    "LoopReport",
    "default_eval_runner",
]
