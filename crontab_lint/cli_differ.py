"""CLI helper for the `crontab-lint diff` sub-command."""

from __future__ import annotations

import argparse
import sys
from typing import List

from crontab_lint.differ import diff


def build_diff_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the `diff` sub-command on *subparsers*."""
    p = subparsers.add_parser(
        "diff",
        help="Compare two crontab expressions and show what changed.",
    )
    p.add_argument("old", metavar="OLD", help="Original cron expression (quoted).")
    p.add_argument("new", metavar="NEW", help="Updated cron expression (quoted).")
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit output as JSON.",
    )
    p.set_defaults(func=run_diff)


def run_diff(args: argparse.Namespace) -> int:
    """Execute the diff command and print results. Returns exit code."""
    result = diff(args.old, args.new)

    if not result.is_valid:
        for err in result.errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    if getattr(args, "json", False):
        import json

        payload = {
            "old_expression": result.old_expression,
            "new_expression": result.new_expression,
            "has_changes": result.has_changes,
            "changed_fields": [
                {
                    "field": fd.field,
                    "old_value": fd.old_value,
                    "new_value": fd.new_value,
                    "old_explanation": fd.old_explanation,
                    "new_explanation": fd.new_explanation,
                }
                for fd in result.changed_fields
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if not result.has_changes:
        print("No differences found — expressions are equivalent.")
        return 0

    print(f"Comparing:")
    print(f"  old: {result.old_expression}")
    print(f"  new: {result.new_expression}")
    print()
    for fd in result.changed_fields:
        print(f"  [{fd.field}]")
        print(f"    - {fd.old_value!r:12s}  {fd.old_explanation}")
        print(f"    + {fd.new_value!r:12s}  {fd.new_explanation}")

    return 0
