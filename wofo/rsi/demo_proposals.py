"""Built-in demo proposals so the RSI loop can be exercised without an
LLM call.

Three proposals against `wofo/evals/rubric.py`:

1. **GOOD** — improves the heuristic by recognizing "13F-HR" as a
   provenance signal. This raises the rubric score on well-sourced
   notes. Should be classified IMPROVE.
2. **BAD** — replaces `_h_provenance` with `return 0`. Should be
   classified REGRESS.
3. **NEUTRAL** — adds a comment but changes no behavior. Should be
   classified INCONCLUSIVE.
"""
from __future__ import annotations

from pathlib import Path

from .proposal import Proposal
from .proposers import MockProposer


REPO = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO / path).read_text()


def _good_proposal() -> Proposal:
    """Make _h_concrete_numbers actually reward concrete numbers.

    The current heuristic divides the raw count of $/percent/shares
    matches by 2 before capping at 3, so a note with 3-4 specific
    figures still scores only 1-2 of 3. That penalizes well-sourced
    notes. Replace `raw // 2` with `min(raw, 3)` so each concrete
    figure contributes one point, capped at the rubric ceiling.
    """
    src = _read("wofo/evals/rubric.py")
    needle_old = (
        "def _h_concrete_numbers(text: str) -> int:\n"
        "    n_dollars = len(re.findall(r\"\\$\\d\", text))\n"
        "    n_pcts    = len(re.findall(r\"\\d+\\.?\\d*%\", text))\n"
        "    n_shares  = len(re.findall(r\"\\bshares?\\b\", text, re.I))\n"
        "    raw = n_dollars + n_pcts + n_shares\n"
        "    return min(raw // 2, 3)"
    )
    needle_new = (
        "def _h_concrete_numbers(text: str) -> int:\n"
        "    # Award one point per specific figure (dollar / percent / share),\n"
        "    # capped at 3. The previous //2 division under-counted well-sourced notes.\n"
        "    n_dollars = len(re.findall(r\"\\$\\s?\\d\", text))\n"
        "    n_pcts    = len(re.findall(r\"\\d+\\.?\\d*%\", text))\n"
        "    n_shares  = len(re.findall(r\"\\bshares?\\b\", text, re.I))\n"
        "    raw = n_dollars + n_pcts + n_shares\n"
        "    return min(raw, 3)"
    )
    if needle_old not in src:
        raise RuntimeError("good_proposal: anchor for replacement not found; rubric has drifted")
    return Proposal(
        label="rubric_concrete_numbers_tighter",
        target_path="wofo/evals/rubric.py",
        new_content=src.replace(needle_old, needle_new),
        rationale="Reward each concrete figure (dollar amount, percent, share count) with one point instead of one-per-two. Lifts the score on quantitatively grounded notes without affecting empty / vague ones.",
        proposer="demo:good",
    )


def _bad_proposal() -> Proposal:
    """Provenance heuristic returns 0 always — guaranteed regression."""
    src = _read("wofo/evals/rubric.py")
    needle_old = (
        "def _h_provenance(text: str) -> int:\n"
        '    """Does the note cite filings or sources?"""\n'
        "    score = 0\n"
        "    if re.search(r\"\\baccession\\b|\\bCIK\\b|\\bEDGAR\\b\", text, re.I): score += 1\n"
        "    if re.search(r\"13F|13-F|13F-HR\", text, re.I): score += 1\n"
        "    if re.search(r\"\\b\\d{4}-\\d{2}-\\d{2}\\b\", text): score += 1\n"
        "    return min(score, 3)"
    )
    needle_new = (
        "def _h_provenance(text: str) -> int:\n"
        '    """Does the note cite filings or sources? (BROKEN: always 0)"""\n'
        "    return 0   # <-- regression"
    )
    return Proposal(
        label="rubric_provenance_broken",
        target_path="wofo/evals/rubric.py",
        new_content=src.replace(needle_old, needle_new),
        rationale="Strawman: removes provenance scoring entirely. Should be flagged REGRESS by the judge.",
        proposer="demo:bad",
    )


def _neutral_proposal() -> Proposal:
    """Comment-only change. Should be INCONCLUSIVE."""
    src = _read("wofo/evals/rubric.py")
    if "# Heuristic detectors" in src:
        new = src.replace(
            "# --- Heuristic detectors ----------------------------------------------------",
            "# --- Heuristic detectors ----------------------------------------------------\n"
            "# (no behavior change; just clarifying the intent of these functions.)",
            1,
        )
    else:
        new = src + "\n# trivial comment\n"
    return Proposal(
        label="rubric_comment_only",
        target_path="wofo/evals/rubric.py",
        new_content=new,
        rationale="Comment-only change. Should produce no measurable eval delta.",
        proposer="demo:neutral",
    )


def demo_proposer() -> MockProposer:
    return MockProposer([_good_proposal(), _bad_proposal(), _neutral_proposal()])
