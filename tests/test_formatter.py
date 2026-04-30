"""Tests for crontab_lint.formatter (text and JSON output, including schedule)."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from crontab_lint.validator import ValidationResult
from crontab_lint.schedule import ScheduleResult
from crontab_lint.formatter import TextFormatter, JsonFormatter


@pytest.fixture
def valid_result() -> ValidationResult:
    return ValidationResult(
        expression="0 9 * * 1",
        valid=True,
        error=None,
        warnings=[],
        explanation="At 09:00 on Monday.",
    )


@pytest.fixture
def invalid_result() -> ValidationResult:
    return ValidationResult(
        expression="99 * * * *",
        valid=False,
        error="Minute value 99 out of range.",
        warnings=[],
        explanation=None,
    )


@pytest.fixture
def sample_schedule() -> ScheduleResult:
    runs = [
        datetime(2024, 1, 15, 9, 0),
        datetime(2024, 1, 22, 9, 0),
    ]
    return ScheduleResult(expression="0 9 * * 1", next_runs=runs)


class TestTextFormatter:
    def test_valid_no_explanation(self, valid_result):
        result = valid_result
        result.explanation = None
        out = TextFormatter().format(result)
        assert "[OK]" in out
        assert "0 9 * * 1" in out

    def test_invalid_shows_error(self, invalid_result):
        out = TextFormatter().format(invalid_result)
        assert "[INVALID]" in out
        assert "out of range" in out

    def test_explanation_shown(self, valid_result):
        out = TextFormatter().format(valid_result)
        assert "Meaning" in out
        assert "09:00" in out

    def test_schedule_shown_in_text(self, valid_result, sample_schedule):
        out = TextFormatter().format(valid_result, schedule=sample_schedule)
        assert "Next runs" in out
        assert "2024-01-15 09:00" in out

    def test_no_schedule_no_next_runs_section(self, valid_result):
        out = TextFormatter().format(valid_result, schedule=None)
        assert "Next runs" not in out


class TestJsonFormatter:
    def test_valid_json_structure(self, valid_result):
        out = JsonFormatter().format(valid_result)
        data = json.loads(out)
        assert data["valid"] is True
        assert data["expression"] == "0 9 * * 1"

    def test_invalid_json_has_error(self, invalid_result):
        out = JsonFormatter().format(invalid_result)
        data = json.loads(out)
        assert data["valid"] is False
        assert "error" in data

    def test_schedule_included_in_json(self, valid_result, sample_schedule):
        out = JsonFormatter().format(valid_result, schedule=sample_schedule)
        data = json.loads(out)
        assert "schedule" in data
        assert len(data["schedule"]["next_runs"]) == 2

    def test_no_schedule_key_when_omitted(self, valid_result):
        out = JsonFormatter().format(valid_result)
        data = json.loads(out)
        assert "schedule" not in data
