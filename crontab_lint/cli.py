"""Command-line interface for crontab-lint."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from crontab_lint.parser import parse
from crontab_lint.validator import validate
from crontab_lint.explainer import explain
from crontab_lint.schedule import next_schedule
from crontab_lint.formatter import JsonFormatter, TextFormatter


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Validate and explain crontab expressions.",
    )
    p.add_argument("expressions", nargs="*", metavar="EXPRESSION",
                   help="One or more cron expressions to validate.")
    p.add_argument("-f", "--file", metavar="FILE",
                   help="Read expressions from a file (one per line).")
    p.add_argument("--no-explain", action="store_true",
                   help="Skip human-readable explanation.")
    p.add_argument("--schedule", action="store_true",
                   help="Show next N scheduled run times.")
    p.add_argument("--schedule-count", type=int, default=5, metavar="N",
                   help="Number of next runs to display (default: 5).")
    p.add_argument("--json", action="store_true",
                   help="Output results as JSON.")
    return p


def _process_expression(
    expr: str,
    no_explain: bool = False,
    show_schedule: bool = False,
    schedule_count: int = 5,
    use_json: bool = False,
) -> tuple[str, bool]:
    parsed = parse(expr)
    result = validate(parsed)
    if not no_explain and result.valid:
        result.explanation = explain(parsed)
    schedule = None
    if show_schedule:
        schedule = next_schedule(parsed, count=schedule_count)
    formatter = JsonFormatter() if use_json else TextFormatter()
    output = formatter.format(result, schedule=schedule)
    return output, result.valid


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions or [])

    if args.file:
        try:
            with open(args.file) as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        expressions.append(line)
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help()
        return 0

    exit_code = 0
    for expr in expressions:
        output, valid = _process_expression(
            expr,
            no_explain=args.no_explain,
            show_schedule=args.schedule,
            schedule_count=args.schedule_count,
            use_json=args.json,
        )
        print(output)
        if not valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
