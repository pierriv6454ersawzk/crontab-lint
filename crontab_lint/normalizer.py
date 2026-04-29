"""Normalize crontab expressions by expanding aliases and cleaning up syntax."""

from dataclasses import dataclass
from typing import Optional

# Maps common aliases to their canonical cron expressions
_ALIAS_MAP = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}

# Maps named month/weekday values to numeric equivalents
_MONTH_NAMES = {
    "jan": "1", "feb": "2", "mar": "3", "apr": "4",
    "may": "5", "jun": "6", "jul": "7", "aug": "8",
    "sep": "9", "oct": "10", "nov": "11", "dec": "12",
}

_WEEKDAY_NAMES = {
    "sun": "0", "mon": "1", "tue": "2", "wed": "3",
    "thu": "4", "fri": "5", "sat": "6",
}


@dataclass
class NormalizeResult:
    original: str
    normalized: str
    was_alias: bool
    changes: list[str]


def _expand_alias(expression: str) -> Optional[str]:
    """Return the canonical form if expression is an alias, else None."""
    return _ALIAS_MAP.get(expression.lower())


def _normalize_names(field: str, name_map: dict[str, str]) -> tuple[str, bool]:
    """Replace named values with numeric equivalents in a field token."""
    result = field.lower()
    changed = False
    for name, num in name_map.items():
        if name in result:
            result = result.replace(name, num)
            changed = True
    return result, changed


def _normalize_slash_one(field: str) -> tuple[str, bool]:
    """Replace redundant /1 step expressions with *."""
    if field.endswith("/1") and "/" in field:
        base = field[: field.rfind("/1")]
        if base == "*" or base.startswith("*"):
            return "*", True
    return field, False


def normalize(expression: str) -> NormalizeResult:
    """Normalize a crontab expression, returning a NormalizeResult."""
    expression = expression.strip()
    changes: list[str] = []

    alias_expansion = _expand_alias(expression)
    if alias_expansion:
        return NormalizeResult(
            original=expression,
            normalized=alias_expansion,
            was_alias=True,
            changes=[f"Expanded alias '{expression}' to '{alias_expansion}'"],
        )

    parts = expression.split()
    if len(parts) != 5:
        return NormalizeResult(
            original=expression, normalized=expression, was_alias=False, changes=[]
        )

    minute, hour, dom, month, dow = parts

    month, month_changed = _normalize_names(month, _MONTH_NAMES)
    if month_changed:
        changes.append(f"Replaced month name with number in '{parts[3]}' -> '{month}'")

    dow, dow_changed = _normalize_names(dow, _WEEKDAY_NAMES)
    if dow_changed:
        changes.append(f"Replaced weekday name with number in '{parts[4]}' -> '{dow}'")

    minute, min_changed = _normalize_slash_one(minute)
    if min_changed:
        changes.append("Removed redundant /1 step in minute field")

    hour, hr_changed = _normalize_slash_one(hour)
    if hr_changed:
        changes.append("Removed redundant /1 step in hour field")

    normalized = " ".join([minute, hour, dom, month, dow])
    return NormalizeResult(
        original=expression, normalized=normalized, was_alias=False, changes=changes
    )
