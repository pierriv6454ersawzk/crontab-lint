"""Human-readable explanations for parsed crontab expressions."""

from typing import List
from .parser import ParseResult, CronField

# Weekday names for human-readable output
WEEKDAY_NAMES = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",  # 7 is also Sunday in some implementations
}

# Month names for human-readable output
MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def _ordinal(n: int) -> str:
    """Return ordinal string for a given integer (e.g., 1 -> '1st')."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _explain_field(field: CronField, field_name: str, name_map: dict = None) -> str:
    """Generate a human-readable explanation for a single cron field.

    Args:
        field: The parsed CronField object.
        field_name: Descriptive name for the field (e.g., 'minute', 'hour').
        name_map: Optional mapping from numeric values to names (e.g., month names).

    Returns:
        A human-readable string describing when this field triggers.
    """
    raw = field.raw

    if raw == "*":
        return f"every {field_name}"

    def label(val: int) -> str:
        if name_map and val in name_map:
            return name_map[val]
        return str(val)

    # Step over all values: */n
    if raw.startswith("*/"):
        step = raw[2:]
        return f"every {step} {field_name}s"

    # Range with optional step: a-b or a-b/n
    if "-" in raw and "/" in raw:
        range_part, step = raw.split("/", 1)
        start, end = range_part.split("-", 1)
        return (
            f"every {step} {field_name}s from {label(int(start))} through {label(int(end))}"
        )

    if "-" in raw:
        start, end = raw.split("-", 1)
        return f"every {field_name} from {label(int(start))} through {label(int(end))}"

    # List of values
    if "," in raw:
        parts = [label(int(v)) for v in raw.split(",")]
        if len(parts) == 2:
            return f"at {field_name}s {parts[0]} and {parts[1]}"
        joined = ", ".join(parts[:-1]) + f", and {parts[-1]}"
        return f"at {field_name}s {joined}"

    # Single value
    try:
        val = int(raw)
        if field_name == "minute":
            return f"at minute {val}"
        if field_name == "hour":
            hour_12 = val % 12 or 12
            period = "AM" if val < 12 else "PM"
            return f"at {hour_12}:00 {period}"
        return f"on {field_name} {label(val)}"
    except ValueError:
        return f"{field_name} '{raw}'"


def explain(result: ParseResult) -> str:
    """Generate a full human-readable explanation of a parsed cron expression.

    Args:
        result: A successfully parsed ParseResult.

    Returns:
        A descriptive string explaining when the cron job will run.

    Raises:
        ValueError: If the ParseResult contains errors.
    """
    if result.errors:
        raise ValueError(
            f"Cannot explain an invalid cron expression: {'; '.join(result.errors)}"
        )

    minute_str = _explain_field(result.minute, "minute")
    hour_str = _explain_field(result.hour, "hour")
    dom_str = _explain_field(result.day_of_month, "day-of-month")
    month_str = _explain_field(result.month, "month", MONTH_NAMES)
    dow_str = _explain_field(result.day_of_week, "day-of-week", WEEKDAY_NAMES)

    parts: List[str] = []

    # Build time description
    if result.minute.raw == "*" and result.hour.raw == "*":
        parts.append("every minute")
    elif result.minute.raw == "*":
        parts.append(f"every minute of {hour_str}")
    else:
        parts.append(f"{minute_str} past {hour_str}")

    # Date constraints
    if result.day_of_month.raw != "*":
        parts.append(f"on the {dom_str}")

    if result.month.raw != "*":
        parts.append(f"in {month_str}")

    if result.day_of_week.raw != "*":
        parts.append(f"on {dow_str}")

    return ", ".join(parts) + "."
