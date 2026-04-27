"""Apply a proposal in an isolated sandbox and run the eval suite.

The sandbox is a temporary directory containing a *copy* of the wofo
package source tree. We do not run from the live repo because:

1. We don't want a partially-applied proposal to corrupt the working
   tree.
2. We want to run the candidate code in a fresh import context so a
   change to (e.g.) a heuristic actually takes effect.

The sandbox is destroyed at the end of the run. The committed-data
directories under `wofo/data/` are *referenced by absolute path* (not
copied) so we don't duplicate the price cache + 13F filings — the eval
needs them, but they're read-only.
"""
from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .proposal import Proposal


REPO = Path(__file__).resolve().parents[2]


@dataclass
class SandboxResult:
    proposal: Proposal
    eval_payload: dict | None
    error: str | None
    sandbox_dir: str


def run_in_sandbox(
    proposal: Proposal,
    eval_runner: Callable[[Path], dict],
    *,
    keep: bool = False,
) -> SandboxResult:
    """Apply `proposal` to a temp tree and call `eval_runner(sandbox_root)`.

    `eval_runner` must be a callable that runs the eval suite given a
    path to the sandbox repo root and returns the eval payload as a
    plain dict. It must not mutate the live repo state.
    """
    sandbox = Path(tempfile.mkdtemp(prefix="wofo-rsi-"))
    try:
        # Copy the wofo package + tests so the candidate code is isolated.
        # We deliberately do NOT copy `wofo/data/` (large) or `.git`.
        for sub in ("wofo", "tests"):
            src = REPO / sub
            if not src.exists():
                continue
            dst = sandbox / sub
            shutil.copytree(
                src, dst,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "data"),
            )
        # Symlink the data dir so price/13f caches are visible without copying.
        data_link = sandbox / "wofo" / "data"
        data_link.parent.mkdir(parents=True, exist_ok=True)
        if not data_link.exists():
            data_link.symlink_to(REPO / "wofo" / "data")

        # Apply the proposal.
        target = sandbox / proposal.target_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(proposal.new_content)

        # Run the eval. We invoke as a subprocess to guarantee a fresh
        # interpreter (no cached imports of the live wofo).
        payload = _run_eval_subprocess(sandbox, eval_runner)
        return SandboxResult(proposal=proposal, eval_payload=payload, error=None, sandbox_dir=str(sandbox))
    except Exception as e:
        return SandboxResult(proposal=proposal, eval_payload=None, error=f"{type(e).__name__}: {e}", sandbox_dir=str(sandbox))
    finally:
        if not keep:
            shutil.rmtree(sandbox, ignore_errors=True)


def _run_eval_subprocess(sandbox: Path, eval_runner: Callable[[Path], dict]) -> dict:
    """Run `eval_runner` in a fresh interpreter pointing PYTHONPATH at sandbox."""
    runner_module = eval_runner.__module__
    runner_name = eval_runner.__qualname__
    result_path = sandbox / "_eval_result.json"
    code = (
        "import importlib, json, sys\n"
        f"sys.path.insert(0, {str(sandbox)!r})\n"
        f"mod = importlib.import_module({runner_module!r})\n"
        f"fn = getattr(mod, {runner_name!r})\n"
        f"out = fn({str(sandbox)!r})\n"
        f"open({str(result_path)!r}, 'w').write(json.dumps(out, default=str))\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(sandbox),
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"sandbox eval failed (rc={proc.returncode}):\n"
            f"--- stdout ---\n{proc.stdout[-2000:]}\n"
            f"--- stderr ---\n{proc.stderr[-2000:]}"
        )
    return json.loads(result_path.read_text())
