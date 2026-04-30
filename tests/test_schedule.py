"""Tests for crontab_lint.schedule."""

from datetime import datetime

import pytest

from crontab_lint.parser import parse
from crontab_lint.schedule import ScheduleResult, next_schedule


FIXED_NOW = datetime(2024, 1, 15, 12, 0, 0)  # Monday


def _parse_ok(expr: str):
    result = parse(expr)
    assert result.ok, f"Expected valid parse for {expr!r}"
    return result


def test_returns_schedule_result():
    parsed = _parse_ok("* * * * *")
    result = next_schedule(parsed, after=FIXED_NOW)
    assert isinstance(result, ScheduleResult)


def test_every_minute_returns_five_runs():
    parsed = _parse_ok("* * * * *")
    result = next_schedule(parsed, after=FIXED_NOW, count=5)
    assert result.ok
    assert len(result.next_runs) == 5


def test_every_minute_first_run_is_next_minute():
    parsed = _parse_ok("* * * * *")
    result = next_schedule(parsed, after=FIXED_NOW)
    expected_first = datetime(2024, 1, 15, 12, 1, 0)
    assert result.next_runs[0] == expected_first


def test_every_minute_runs_are_consecutive():
    parsed = _parse_ok("* * * * *")
    result = next_schedule(parsed, after=FIXED_NOW, count=3)
    diffs = [
        (result.next_runs[i + 1] - result.next_runs[i]).seconds
        for i in range(len(result.next_runs) - 1)
    ]
    assert all(d == 60 for d in diffs)


def test_hourly_returns_correct_times():
    parsed = _parse_ok("0 * * * *")
    result = next_schedule(parsed, after=FIXED_NOW, count=3)
    assert result.ok
    for run in result.next_runs:
        assert run.minute == 0


def test_daily_midnight_next_run():
    parsed = _parse_ok("0 0 * * *")
    result = next_schedule(parsed, after=FIXED_NOW, count=1)
    assert result.ok
    assert result.next_runs[0] == datetime(2024, 1, 16, 0, 0, 0)


def test_specific_time_expression():
    parsed = _parse_ok("30 9 * * *")
    result = next_schedule(parsed, after=FIXED_NOW, count=1)
    assert result.ok
    assert result.next_runs[0] == datetime(2024, 1, 15, 9, 30, 0)


def test_invalid_parse_returns_error():
    parsed = parse("99 * * * *")
    result = next_schedule(parsed)
    assert not result.ok
    assert result.error is not None
    assert result.next_runs == []


def test_custom_count():
    parsed = _parse_ok("* * * * *")
    result = next_schedule(parsed, after=FIXED_NOW, count=10)
    assert len(result.next_runs) == 10


def test_expression_preserved():
    expr = "0 12 * * 1"
    parsed = _parse_ok(expr)
    result = next_schedule(parsed, after=FIXED_NOW)
    assert result.expression == expr


def test_weekly_monday_noon_next_run():
    """Verify that a weekly Monday-at-noon job schedules correctly.

    FIXED_NOW is already Monday at 12:00:00, so the next run should be
    the following Monday (2024-01-22) at 12:00.
    """
    parsed = _parse_ok("0 12 * * 1")
    result = next_schedule(parsed, after=FIXED_NOW, count=1)
    assert result.ok
    assert result.next_runs[0] == datetime(2024, 1, 22, 12, 0, 0)
