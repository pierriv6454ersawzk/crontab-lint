"""CLI sub-command: summarize a file of crontab expressions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from crontab_lint.summarizer import summarize


def build_summary_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "summarize",
        help="Print a statistical summary for a file of crontab expressions.",
    )
    p.add_argument("file", type=Path, help="File containing one expression per line.")
    p.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Output summary as JSON.",
    )
    p.set_defaults(func=run_summary)


def run_summary(args: argparse.Namespace) -> int:
    path: Path = args.file
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 2

    expressions: List[str] = path.read_text().splitlines()
    result = summarize(expressions)

    if args.as_json:
        data = {
            "total": result.total,
            "valid": result.valid,
            "invalid": result.invalid,
            "with_suggestions": result.with_suggestions,
            "valid_pct": result.valid_pct,
            "invalid_pct": result.invalid_pct,
            "suggestion_pct": result.suggestion_pct,
            "invalid_expressions": result.invalid_expressions,
            "suggestion_expressions": result.suggestion_expressions,
        }
        print(json.dumps(data, indent=2))
    else:
        print(f"Total      : {result.total}")
        print(f"Valid      : {result.valid} ({result.valid_pct}%)")
        print(f"Invalid    : {result.invalid} ({result.invalid_pct}%)")
        print(f"Suggestions: {result.with_suggestions} ({result.suggestion_pct}%)")
        if result.invalid_expressions:
            print("\nInvalid expressions:")
            for expr in result.invalid_expressions:
                print(f"  {expr}")
        if result.suggestion_expressions:
            print("\nExpressions with suggestions:")
            for expr in result.suggestion_expressions:
                print(f"  {expr}")

    return 1 if result.invalid else 0
