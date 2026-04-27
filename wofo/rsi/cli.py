"""CLI entry point for the RSI loop.

    python -m wofo.rsi.cli demo          # run the built-in demo with mock proposals
    python -m wofo.rsi.cli file <path>   # load proposals from JSON file
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import default_eval_runner   # populated below
from .loop import run_loop
from .proposers import FileProposer, MockProposer
from .demo_proposals import demo_proposer


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="wofo.rsi")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="Run with built-in mock proposals")
    fp = sub.add_parser("file", help="Run with proposals from a JSON file")
    fp.add_argument("path")
    args = p.parse_args(argv)

    if args.cmd == "demo":
        proposer = demo_proposer()
    elif args.cmd == "file":
        proposer = FileProposer(args.path)
    else:
        p.print_help()
        sys.exit(1)

    report = run_loop(proposer, default_eval_runner, label=args.cmd)
    print(json.dumps({"verdicts": [o.verdict for o in report.outcomes]}, indent=2))


if __name__ == "__main__":
    main()
