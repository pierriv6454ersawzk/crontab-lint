"""Core parser module for crontab expressions.

Handles tokenization and structural validation of cron expressions,
supporting standard 5-field and extended 6-field (with seconds) formats.
"""

from dataclasses import dataclass, field
from typing import Optional


# Field definitions: (name, min_value, max_value)
CRON_FIELDS = [
    ("minute", 0, 59),
    ("hour", 0, 23),
    ("day_of_month", 1, 31),
    ("month", 1, 12),
    ("day_of_week", 0, 7),  # 0 and 7 both represent Sunday
]

CRON_FIELDS_WITH_SECONDS = [
    ("second", 0, 59),
] + CRON_FIELDS

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

WEEKDAY_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}

SPECIAL_STRINGS = {
    "@yearly":   "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly":  "0 0 1 * *",
    "@weekly":   "0 0 * * 0",
    "@daily":    "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly":   "0 * * * *",
}


@dataclass
class CronField:
    """Represents a single parsed field in a cron expression."""
    name: str
    raw_value: str
    min_val: int
    max_val: int
    errors: list = field(default_factory=list)


@dataclass
class ParseResult:
    """Result of parsing a cron expression."""
    raw_expression: str
    expanded_expression: Optional[str]
    fields: list
    is_valid: bool
    errors: list = field(default_factory=list)
    is_special: bool = False
    special_label: Optional[str] = None


def _resolve_alias(value: str, aliases: dict) -> str:
    """Replace named aliases (e.g. 'jan', 'mon') with their numeric equivalents."""
    result = value.lower()
    for alias, num in aliases.items():
        result = result.replace(alias, str(num))
    return result


def _validate_field_token(token: str, min_val: int, max_val: int) -> list:
    """Validate a single token within a cron field (handles *, ranges, steps, lists)."""
    errors = []

    if token == "*":
        return errors

    # Step values: */n or range/n
    if "/" in token:
        parts = token.split("/", 1)
        if len(parts) != 2 or not parts[1].isdigit():
            errors.append(f"Invalid step syntax: '{token}'")
            return errors
        step = int(parts[1])
        if step < 1:
            errors.append(f"Step value must be >= 1, got {step} in '{token}'")
        base = parts[0]
        if base != "*":
            errors.extend(_validate_field_token(base, min_val, max_val))
        return errors

    # Ranges: n-m
    if "-" in token:
        parts = token.split("-", 1)
        if not parts[0].isdigit() or not parts[1].isdigit():
            errors.append(f"Invalid range syntax: '{token}'")
            return errors
        lo, hi = int(parts[0]), int(parts[1])
        if lo < min_val or lo > max_val:
            errors.append(f"Range start {lo} out of bounds [{min_val}-{max_val}] in '{token}'")
        if hi < min_val or hi > max_val:
            errors.append(f"Range end {hi} out of bounds [{min_val}-{max_val}] in '{token}'")
        if lo > hi:
            errors.append(f"Range start {lo} is greater than end {hi} in '{token}'")
        return errors

    # Plain integer
    if token.isdigit():
        val = int(token)
        if val < min_val or val > max_val:
            errors.append(f"Value {val} out of bounds [{min_val}-{max_val}]")
        return errors

    errors.append(f"Unrecognized token: '{token}'")
    return errors


def _parse_field(raw: str, name: str, min_val: int, max_val: int) -> CronField:
    """Parse and validate a single cron field."""
    cf = CronField(name=name, raw_value=raw, min_val=min_val, max_val=max_val)

    # Resolve month/weekday aliases
    resolved = _resolve_alias(raw, {**MONTH_ALIASES, **WEEKDAY_ALIASES})

    # Handle comma-separated lists
    tokens = resolved.split(",")
    for token in tokens:
        cf.errors.extend(_validate_field_token(token.strip(), min_val, max_val))

    return cf


def parse(expression: str) -> ParseResult:
    """Parse a crontab expression string and return a structured ParseResult."""
    expr = expression.strip()
    special_label = None
    expanded = None

    # Handle special @ strings
    lower_expr = expr.lower()
    if lower_expr in SPECIAL_STRINGS:
        special_label = lower_expr
        expanded = SPECIAL_STRINGS[lower_expr]
        expr = expanded

    parts = expr.split()
    field_defs = CRON_FIELDS_WITH_SECONDS if len(parts) == 6 else CRON_FIELDS

    errors = []
    if len(parts) not in (5, 6):
        errors.append(
            f"Expected 5 or 6 fields, got {len(parts)}. "
            "Format: minute hour day month weekday [or second minute hour day month weekday]"
        )
        return ParseResult(
            raw_expression=expression,
            expanded_expression=expanded,
            fields=[],
            is_valid=False,
            errors=errors,
            is_special=special_label is not None,
            special_label=special_label,
        )

    parsed_fields = [
        _parse_field(parts[i], name, min_v, max_v)
        for i, (name, min_v, max_v) in enumerate(field_defs)
    ]

    all_errors = [e for f in parsed_fields for e in f.errors]
    return ParseResult(
        raw_expression=expression,
        expanded_expression=expanded,
        fields=parsed_fields,
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        is_special=special_label is not None,
        special_label=special_label,
    )
