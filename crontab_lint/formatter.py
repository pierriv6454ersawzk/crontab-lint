"""Formatters for ParseResult / ValidationResult output."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .parser import ParseResult


def _result_to_dict(result: ParseResult, explanation: str | None = None) -> Dict[str, Any]:
    d: Dict[str, Any] = {
        "expression": result.expression,
        "valid": result.valid,
    }
    if result.error:
        d["error"] = result.error
    if explanation:
        d["explanation"] = explanation
    return d


class TextFormatter:
    """Render results as human-readable text."""

    def format(self, result: ParseResult, explanation: str | None = None,
               warnings: List[str] | None = None) -> str:
        lines: List[str] = []
        status = "OK" if result.valid else "INVALID"
        lines.append(f"{result.expression!r:40s}  [{status}]")
        if result.error:
            lines.append(f"  Error   : {result.error}")
        if explanation:
            lines.append(f"  Meaning : {explanation}")
        for w in (warnings or []):
            lines.append(f"  Warning : {w}")
        return "\n".join(lines)


class JsonFormatter:
    """Render results as JSON."""

    def format(self, result: ParseResult, explanation: str | None = None,
               warnings: List[str] | None = None) -> str:
        d = _result_to_dict(result, explanation)
        if warnings:
            d["warnings"] = warnings
        return json.dumps(d, indent=2)


def format_result(result: ParseResult, explanation: str | None = None,
                 warnings: List[str] | None = None,
                 fmt: str = "text") -> str:
    formatter = JsonFormatter() if fmt == "json" else TextFormatter()
    return formatter.format(result, explanation, warnings)


def format_summary(total: int, invalid: int, fmt: str = "text") -> str:
    valid = total - invalid
    if fmt == "json":
        return json.dumps({"total": total, "valid": valid, "invalid": invalid}, indent=2)
    return f"\nSummary: {total} expression(s) — {valid} valid, {invalid} invalid."
