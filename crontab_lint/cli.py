"""Command-line interface for crontab-lint."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from crontab_lint.explainer import explain
from crontab_lint.formatter import get_formatter
from crontab_lint.parser import parse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Validate and explain crontab expressions.",
    )
    p.add_argument("expressions", nargs="*", metavar="EXPRESSION", help="Crontab expression(s) to check.")
    p.add_argument("-f", "--file", metavar="FILE", help="File containing one expression per line.")
    p.add_argument("--explain", action="store_true", default=False, help="Print a human-readable explanation.")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    return p


def _process_expression(
    expression: str,
    *,
    show_explain: bool,
    formatter,
) -> bool:
    """Parse, optionally explain, and print *expression*. Returns True if valid."""
    result = parse(expression)
    explanation = explain(result) if show_explain and result.valid else None
    print(formatter.format_result(expression, result, explanation))
    return result.valid


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: list[str] = list(args.expressions)

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"crontab-lint: file not found: {args.file}", file=sys.stderr)
            return 2
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                expressions.append(line)

    if not expressions:
        parser.print_help()
        return 0

    formatter = get_formatter(args.fmt)
    total = len(expressions)
    invalid = 0

    for expr in expressions:
        ok = _process_expression(expr, show_explain=args.explain, formatter=formatter)
        if not ok:
            invalid += 1

    if total > 1:
        print(formatter.format_summary(total, invalid))

    return 0 if invalid == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
