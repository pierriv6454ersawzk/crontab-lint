"""Output formatters for crontab-lint results."""
from __future__ import annotations

import json
from typing import Any

from crontab_lint.parser import ParseResult


def _result_to_dict(expression: str, result: ParseResult, explanation: str | None = None) -> dict[str, Any]:
    """Convert a ParseResult to a serialisable dictionary."""
    data: dict[str, Any] = {
        "expression": expression,
        "valid": result.valid,
    }
    if result.errors:
        data["errors"] = result.errors
    if explanation is not None:
        data["explanation"] = explanation
    return data


class TextFormatter:
    """Plain-text formatter (default)."""

    def format_result(self, expression: str, result: ParseResult, explanation: str | None = None) -> str:
        lines: list[str] = []
        status = "OK" if result.valid else "INVALID"
        lines.append(f"{expression!r}  [{status}]")
        for error in result.errors:
            lines.append(f"  ERROR: {error}")
        if explanation:
            lines.append(f"  => {explanation}")
        return "\n".join(lines)

    def format_summary(self, total: int, invalid: int) -> str:
        valid = total - invalid
        return f"\nSummary: {total} expression(s) checked — {valid} valid, {invalid} invalid."


class JsonFormatter:
    """JSON formatter (one object per expression, newline-delimited)."""

    def format_result(self, expression: str, result: ParseResult, explanation: str | None = None) -> str:
        data = _result_to_dict(expression, result, explanation)
        return json.dumps(data, ensure_ascii=False)

    def format_summary(self, total: int, invalid: int) -> str:
        summary = {"total": total, "valid": total - invalid, "invalid": invalid}
        return json.dumps(summary, ensure_ascii=False)


def get_formatter(fmt: str) -> TextFormatter | JsonFormatter:
    """Return the appropriate formatter for *fmt* (``'text'`` or ``'json'``)."""
    if fmt == "json":
        return JsonFormatter()
    return TextFormatter()
