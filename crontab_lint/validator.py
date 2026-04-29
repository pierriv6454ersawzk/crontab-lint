"""High-level validation helpers for crontab expressions."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseResult


# Well-known problematic patterns with human-readable warnings
_WARNINGS = [
    (
        lambda r: r.fields[0].raw == "*" and r.fields[1].raw == "*",
        "Runs every minute — this may be unintentionally frequent.",
    ),
    (
        lambda r: any(f.raw.startswith("*/1") for f in r.fields),
        "Using */1 is equivalent to * and adds no value.",
    ),
    (
        lambda r: r.fields[4].raw not in ("*", "0", "7")
        and r.fields[2].raw != "*",
        "Specifying both day-of-month and day-of-week may yield unexpected results.",
    ),
]


@dataclass
class ValidationResult:
    expression: str
    parse_result: ParseResult
    warnings: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.parse_result.valid

    @property
    def error(self) -> Optional[str]:
        return self.parse_result.error


def validate(expression: str) -> ValidationResult:
    """Parse *expression* and attach any lint warnings."""
    result = parse(expression)
    warnings: List[str] = []

    if result.valid:
        for predicate, message in _WARNINGS:
            try:
                if predicate(result):
                    warnings.append(message)
            except Exception:
                pass  # defensive — never crash on a warning check

    return ValidationResult(
        expression=expression,
        parse_result=result,
        warnings=warnings,
    )
