"""Tests for crontab_lint.differ."""

import pytest
from crontab_lint.differ import diff, DiffResult, FieldDiff


def test_diff_returns_diff_result():
    result = diff("0 * * * *", "0 9 * * *")
    assert isinstance(result, DiffResult)


def test_identical_expressions_have_no_changes():
    result = diff("0 9 * * 1", "0 9 * * 1")
    assert result.is_valid
    assert not result.has_changes
    assert result.changed_fields == []


def test_single_field_change_detected():
    result = diff("0 * * * *", "0 9 * * *")
    assert result.is_valid
    assert result.has_changes
    assert len(result.changed_fields) == 1
    changed = result.changed_fields[0]
    assert changed.field == "hour"
    assert changed.old_value == "*"
    assert changed.new_value == "9"


def test_multiple_field_changes_detected():
    result = diff("* * * * *", "0 9 1 * 1")
    assert result.is_valid
    assert len(result.changed_fields) == 3
    changed_names = {fd.field for fd in result.changed_fields}
    assert changed_names == {"minute", "hour", "day-of-month"}


def test_field_diff_contains_explanations():
    result = diff("0 * * * *", "30 * * * *")
    assert result.is_valid
    fd = result.changed_fields[0]
    assert isinstance(fd.old_explanation, str)
    assert isinstance(fd.new_explanation, str)
    assert len(fd.old_explanation) > 0
    assert len(fd.new_explanation) > 0


def test_invalid_old_expression_returns_error():
    result = diff("99 * * * *", "0 * * * *")
    assert not result.is_valid
    assert any("Old expression" in e for e in result.errors)


def test_invalid_new_expression_returns_error():
    result = diff("0 * * * *", "0 25 * * *")
    assert not result.is_valid
    assert any("New expression" in e for e in result.errors)


def test_both_invalid_returns_two_errors():
    result = diff("99 * * * *", "0 25 * * *")
    assert not result.is_valid
    assert len(result.errors) == 2


def test_wrong_field_count_returns_error():
    result = diff("0 * *", "0 * * * *")
    assert not result.is_valid


def test_diff_stores_original_expressions():
    old = "0 0 * * *"
    new = "0 12 * * *"
    result = diff(old, new)
    assert result.old_expression == old
    assert result.new_expression == new


def test_has_changes_false_when_identical():
    result = diff("*/5 * * * *", "*/5 * * * *")
    assert not result.has_changes
