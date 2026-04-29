"""Tests for crontab_lint.validator."""

import pytest
from crontab_lint.validator import validate, ValidationResult


def test_valid_expression_returns_valid():
    result = validate("0 9 * * 1")
    assert result.valid is True
    assert result.error is None


def test_invalid_expression_returns_invalid():
    result = validate("99 9 * * 1")
    assert result.valid is False
    assert result.error is not None


def test_invalid_expression_has_no_warnings():
    result = validate("99 9 * * 1")
    assert result.warnings == []


def test_every_minute_warning():
    result = validate("* * * * *")
    assert result.valid is True
    messages = " ".join(result.warnings)
    assert "every minute" in messages.lower()


def test_slash_one_warning():
    result = validate("*/1 * * * *")
    assert result.valid is True
    assert any("*/1" in w for w in result.warnings)


def test_dom_and_dow_warning():
    result = validate("0 9 15 * 1")
    assert result.valid is True
    assert any("day-of-month" in w for w in result.warnings)


def test_no_spurious_warnings_for_clean_expression():
    result = validate("30 6 * * 1-5")
    assert result.valid is True
    assert result.warnings == []


def test_returns_validation_result_instance():
    result = validate("0 0 1 1 *")
    assert isinstance(result, ValidationResult)


def test_expression_stored_on_result():
    expr = "15 14 1 * *"
    result = validate(expr)
    assert result.expression == expr


def test_parse_result_accessible():
    result = validate("0 12 * * *")
    assert result.parse_result is not None
    assert result.parse_result.valid is True
