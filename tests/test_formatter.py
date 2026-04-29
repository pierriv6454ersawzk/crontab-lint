"""Tests for crontab_lint.formatter."""
import json

import pytest

from crontab_lint.formatter import JsonFormatter, TextFormatter, get_formatter
from crontab_lint.parser import ParseResult


@pytest.fixture()
def valid_result():
    return ParseResult(valid=True, fields={}, errors=[])


@pytest.fixture()
def invalid_result():
    return ParseResult(valid=False, fields={}, errors=["minute value 99 out of range"])


# ---------------------------------------------------------------------------
# TextFormatter
# ---------------------------------------------------------------------------

class TestTextFormatter:
    def test_valid_no_explanation(self, valid_result):
        out = TextFormatter().format_result("0 * * * *", valid_result)
        assert "[OK]" in out
        assert "ERROR" not in out

    def test_invalid_shows_error(self, invalid_result):
        out = TextFormatter().format_result("99 * * * *", invalid_result)
        assert "[INVALID]" in out
        assert "minute value 99 out of range" in out

    def test_explanation_included(self, valid_result):
        out = TextFormatter().format_result("0 * * * *", valid_result, explanation="every hour")
        assert "every hour" in out

    def test_summary(self):
        out = TextFormatter().format_summary(total=5, invalid=2)
        assert "5" in out
        assert "3 valid" in out
        assert "2 invalid" in out


# ---------------------------------------------------------------------------
# JsonFormatter
# ---------------------------------------------------------------------------

class TestJsonFormatter:
    def test_valid_result_json(self, valid_result):
        raw = JsonFormatter().format_result("0 * * * *", valid_result)
        data = json.loads(raw)
        assert data["valid"] is True
        assert data["expression"] == "0 * * * *"
        assert "errors" not in data

    def test_invalid_result_json(self, invalid_result):
        raw = JsonFormatter().format_result("99 * * * *", invalid_result)
        data = json.loads(raw)
        assert data["valid"] is False
        assert len(data["errors"]) == 1

    def test_explanation_in_json(self, valid_result):
        raw = JsonFormatter().format_result("0 * * * *", valid_result, explanation="every hour")
        data = json.loads(raw)
        assert data["explanation"] == "every hour"

    def test_summary_json(self):
        raw = JsonFormatter().format_summary(total=4, invalid=1)
        data = json.loads(raw)
        assert data == {"total": 4, "valid": 3, "invalid": 1}


# ---------------------------------------------------------------------------
# get_formatter factory
# ---------------------------------------------------------------------------

def test_get_formatter_text():
    assert isinstance(get_formatter("text"), TextFormatter)


def test_get_formatter_json():
    assert isinstance(get_formatter("json"), JsonFormatter)


def test_get_formatter_default():
    assert isinstance(get_formatter("unknown"), TextFormatter)
