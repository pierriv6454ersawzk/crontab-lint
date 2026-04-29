"""Tests for crontab_lint.normalizer."""

import pytest
from crontab_lint.normalizer import normalize, NormalizeResult


def test_normalize_returns_result_type():
    result = normalize("0 0 * * *")
    assert isinstance(result, NormalizeResult)


def test_no_changes_leaves_expression_intact():
    expr = "0 0 * * *"
    result = normalize(expr)
    assert result.normalized == expr
    assert result.changes == []
    assert result.was_alias is False


def test_alias_at_daily_expanded():
    result = normalize("@daily")
    assert result.was_alias is True
    assert result.normalized == "0 0 * * *"
    assert len(result.changes) == 1
    assert "@daily" in result.changes[0]


def test_alias_at_hourly_expanded():
    result = normalize("@hourly")
    assert result.normalized == "0 * * * *"
    assert result.was_alias is True


def test_alias_at_yearly_expanded():
    result = normalize("@yearly")
    assert result.normalized == "0 0 1 1 *"


def test_alias_at_annually_same_as_yearly():
    assert normalize("@annually").normalized == normalize("@yearly").normalized


def test_alias_case_insensitive():
    result = normalize("@DAILY")
    assert result.was_alias is True
    assert result.normalized == "0 0 * * *"


def test_month_name_replaced_with_number():
    result = normalize("0 0 1 jan *")
    assert "1" in result.normalized.split()[3]
    assert result.changes


def test_weekday_name_replaced_with_number():
    result = normalize("0 0 * * mon")
    assert result.normalized.split()[4] == "1"
    assert result.changes


def test_month_and_weekday_names_both_replaced():
    result = normalize("0 0 1 dec fri")
    parts = result.normalized.split()
    assert parts[3] == "12"
    assert parts[4] == "5"
    assert len(result.changes) == 2


def test_slash_one_in_minute_removed():
    result = normalize("*/1 0 * * *")
    assert result.normalized.split()[0] == "*"
    assert any("minute" in c for c in result.changes)


def test_slash_one_in_hour_removed():
    result = normalize("0 */1 * * *")
    assert result.normalized.split()[1] == "*"
    assert any("hour" in c for c in result.changes)


def test_non_star_slash_one_not_removed():
    result = normalize("0 0/1 * * *")
    assert result.normalized.split()[1] == "0/1"


def test_invalid_expression_returned_unchanged():
    result = normalize("not a cron")
    assert result.normalized == "not a cron"
    assert result.changes == []
    assert result.was_alias is False


def test_original_preserved_after_normalization():
    expr = "0 0 1 jan *"
    result = normalize(expr)
    assert result.original == expr
