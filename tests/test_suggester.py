"""Tests for crontab_lint.suggester module."""

import pytest

from crontab_lint.suggester import suggest, Suggestion, SuggestionResult
from crontab_lint.validator import valid, error, ValidationResult


@pytest.fixture
def clean_validation() -> ValidationResult:
    return valid("* * * * *")


def test_suggest_returns_suggestion_result(clean_validation):
    result = suggest("* * * * *", clean_validation)
    assert isinstance(result, SuggestionResult)
    assert result.original == "* * * * *"


def test_suggest_alias_every_minute(clean_validation):
    result = suggest("* * * * *", clean_validation)
    aliases = [s.replacement for s in result.suggestions if s.replacement]
    assert "@every-minute" in aliases


def test_suggest_alias_daily():
    v = valid("0 0 * * *")
    result = suggest("0 0 * * *", v)
    aliases = [s.replacement for s in result.suggestions if s.replacement]
    assert "@daily" in aliases


def test_suggest_alias_hourly():
    v = valid("0 * * * *")
    result = suggest("0 * * * *", v)
    aliases = [s.replacement for s in result.suggestions if s.replacement]
    assert "@hourly" in aliases


def test_no_suggestion_for_non_standard(clean_validation):
    result = suggest("5 4 * * *", clean_validation)
    alias_suggestions = [s for s in result.suggestions if s.replacement]
    assert alias_suggestions == []


def test_slash_one_suggestion():
    v = valid("*/1 * * * *")
    result = suggest("*/1 * * * *", v)
    messages = [s.message for s in result.suggestions]
    assert any("/1" in m for m in messages)


def test_no_slash_one_suggestion_when_absent():
    v = valid("*/5 * * * *")
    result = suggest("*/5 * * * *", v)
    slash_one = [s for s in result.suggestions if "/1" in s.message]
    assert slash_one == []


def test_warnings_become_suggestions():
    v = ValidationResult(
        expression="* * * * *",
        is_valid=True,
        error=None,
        warnings=["Runs every minute — high frequency"],
    )
    result = suggest("* * * * *", v)
    warning_suggestions = [s for s in result.suggestions if "Warning:" in s.message]
    assert len(warning_suggestions) == 1


def test_has_suggestions_true_when_suggestions_exist(clean_validation):
    result = suggest("* * * * *", clean_validation)
    assert result.has_suggestions is True


def test_has_suggestions_false_when_no_suggestions():
    v = valid("30 6 * * 1-5")
    result = suggest("30 6 * * 1-5", v)
    assert result.has_suggestions is False
