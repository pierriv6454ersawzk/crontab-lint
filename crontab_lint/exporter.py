"""Export parsed crontab results to various file formats."""
from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, dataclass
from typing import List, Optional

from crontab_lint.validator import ValidationResult
from crontab_lint.normalizer import NormalizeResult


@dataclass
class ExportRow:
    expression: str
    valid: bool
    normalized: Optional[str]
    warnings: List[str]
    errors: List[str]


def _build_row(expression: str, result: ValidationResult, norm: Optional[NormalizeResult] = None) -> ExportRow:
    normalized_expr = norm.normalized if norm and norm.changed else None
    return ExportRow(
        expression=expression,
        valid=result.valid,
        normalized=normalized_expr,
        warnings=list(result.warnings),
        errors=list(result.errors),
    )


def export_json(rows: List[ExportRow], indent: int = 2) -> str:
    """Serialize export rows to a JSON string."""
    data = [
        {
            "expression": r.expression,
            "valid": r.valid,
            "normalized": r.normalized,
            "warnings": r.warnings,
            "errors": r.errors,
        }
        for r in rows
    ]
    return json.dumps(data, indent=indent)


def export_csv(rows: List[ExportRow]) -> str:
    """Serialize export rows to a CSV string."""
    output = io.StringIO()
    fieldnames = ["expression", "valid", "normalized", "warnings", "errors"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "expression": row.expression,
            "valid": row.valid,
            "normalized": row.normalized or "",
            "warnings": "|".join(row.warnings),
            "errors": "|".join(row.errors),
        })
    return output.getvalue()


def export_summary(rows: List[ExportRow]) -> str:
    """Return a plain-text summary of validation results.

    Prints counts of valid/invalid expressions and lists any errors or
    warnings grouped by expression.

    Args:
        rows: Export rows produced by :func:`export`.

    Returns:
        A human-readable summary string.
    """
    valid_count = sum(1 for r in rows if r.valid)
    invalid_count = len(rows) - valid_count
    lines = [
        f"Total: {len(rows)}  Valid: {valid_count}  Invalid: {invalid_count}",
    ]
    for row in rows:
        if row.errors or row.warnings:
            lines.append(f"  {row.expression}")
            for err in row.errors:
                lines.append(f"    ERROR:   {err}")
            for warn in row.warnings:
                lines.append(f"    WARNING: {warn}")
    return "\n".join(lines)


def export(expressions: List[str], fmt: str = "json") -> str:
    """Validate and export a list of crontab expressions.

    Args:
        expressions: Raw crontab expression strings.
        fmt: Output format, one of ``'json'``, ``'csv'``, or ``'summary'``.

    Returns:
        Formatted string in the requested format.
    """
    from crontab_lint.validator import validate
    from crontab_lint.normalizer import normalize

    rows: List[ExportRow] = []
    for expr in expressions:
        vr = validate(expr)
        nr = normalize(expr) if vr.valid else None
        rows.append(_build_row(expr, vr, nr))

    if fmt == "csv":
        return export_csv(rows)
    if fmt == "summary":
        return export_summary(rows)
    return export_json(rows)
