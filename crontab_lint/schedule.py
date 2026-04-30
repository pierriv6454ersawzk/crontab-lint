"""Human-readable next-run schedule calculator for cron expressions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from crontab_lint.parser import ParseResult


@dataclass
class ScheduleResult:
    expression: str
    next_runs: List[datetime]
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


def _matches_field(value: int, field_values: List[int]) -> bool:
    return value in field_values


def _next_runs(
    parsed: ParseResult,
    after: datetime,
    count: int = 5,
) -> List[datetime]:
    """Return the next *count* datetimes that match the parsed cron fields."""
    results: List[datetime] = []
    # Start from the next whole minute
    current = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    # Safety cap: search up to ~4 years of minutes
    max_iterations = 60 * 24 * 366 * 4
    iterations = 0

    minute_vals = parsed.fields[0].values
    hour_vals = parsed.fields[1].values
    dom_vals = parsed.fields[2].values
    month_vals = parsed.fields[3].values
    dow_vals = parsed.fields[4].values

    while len(results) < count and iterations < max_iterations:
        iterations += 1
        if (
            _matches_field(current.month, month_vals)
            and _matches_field(current.day, dom_vals)
            and _matches_field(current.weekday() + 1 if current.weekday() < 6 else 0, dow_vals)
            and _matches_field(current.hour, hour_vals)
            and _matches_field(current.minute, minute_vals)
        ):
            results.append(current)
            current += timedelta(minutes=1)
        else:
            current += timedelta(minutes=1)

    return results


def next_schedule(
    parsed: ParseResult,
    after: Optional[datetime] = None,
    count: int = 5,
) -> ScheduleResult:
    """Compute the next scheduled datetimes for a successfully parsed expression."""
    if not parsed.ok:
        return ScheduleResult(
            expression=parsed.expression,
            next_runs=[],
            error="Cannot compute schedule for invalid expression.",
        )
    after = after or datetime.now()
    runs = _next_runs(parsed, after, count)
    return ScheduleResult(expression=parsed.expression, next_runs=runs)
