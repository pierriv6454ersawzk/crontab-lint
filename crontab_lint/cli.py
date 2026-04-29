"""Command-line interface for crontab-lint."""

import argparse
import sys
from typing import List, Optional

from crontab_lint.parser import parse
from crontab_lint.explainer import explain


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Validate and explain crontab expressions.",
    )
    parser.add_argument(
        "expression",
        nargs="?",
        help="Crontab expression to validate (e.g. '*/5 * * * *').",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Path to a crontab file; each non-comment line is validated.",
    )
    parser.add_argument(
        "--no-explain",
        action="store_true",
        help="Suppress human-readable explanation; only show errors.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if any warnings are present.",
    )
    return parser


def _process_expression(expr: str, no_explain: bool) -> bool:
    """Validate and optionally explain a single expression.
    Returns True if valid (no errors), False otherwise."""
    result = parse(expr)
    if result.errors:
        print(f"INVALID: {expr}")
        for err in result.errors:
            print(f"  error: {err}")
        return False

    if not no_explain:
        print(f"OK: {expr}")
        print(f"  {explain(result)}")
    else:
        print(f"OK: {expr}")
    return True


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.expression and not args.file:
        parser.print_help()
        return 0

    all_valid = True

    if args.file:
        try:
            with open(args.file) as fh:
                lines = fh.readlines()
        except OSError as exc:
            print(f"crontab-lint: cannot open file: {exc}", file=sys.stderr)
            return 2

        for raw in lines:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if not _process_expression(line, args.no_explain):
                all_valid = False
    elif args.expression:
        if not _process_expression(args.expression, args.no_explain):
            all_valid = False

    return 0 if all_valid else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
