"""Tests for crontab_lint.ranker."""
import pytest
from unittest.mock import MagicMock

from crontab_lint.ranker import rank, RankResult
from crontab_lint.validator import ValidationResult
from crontab_lint.suggester import SuggestionResult


def _make_valid(warnings=None):
    return ValidationResult(valid=True, expression="", errors=[], warnings=warnings or [])


def _make_invalid():
    return ValidationResult(valid=False, expression="", errors=["bad"], warnings=[])


def _no_suggestions():
    return SuggestionResult(has_suggestions=False, suggestions=[])


def _with_suggestions():
    return SuggestionResult(has_suggestions=True, suggestions=[MagicMock()])


def test_rank_returns_rank_result():
    result = rank("0 * * * *", _make_valid(), _no_suggestions())
    assert isinstance(result, RankResult)


def test_invalid_expression_scores_ten():
    result = rank("bad", _make_invalid(), _no_suggestions())
    assert result.score == 10
    assert result.level == "risky"
    assert any("invalid" in r.lower() for r in result.reasons)


def test_every_minute_is_risky():
    result = rank("* * * * *", _make_valid(), _no_suggestions())
    assert result.score >= 4
    assert result.level in ("complex", "risky")


def test_simple_daily_scores_low():
    result = rank("0 9 * * *", _make_valid(), _no_suggestions())
    assert result.score < 3
    assert result.level == "simple"


def test_list_field_increases_score():
    base = rank("0 9 * * *", _make_valid(), _no_suggestions())
    with_list = rank("0 9,12 * * *", _make_valid(), _no_suggestions())
    assert with_list.score > base.score


def test_dom_and_dow_both_set_increases_score():
    result = rank("0 9 1 * 1", _make_valid(), _no_suggestions())
    assert result.score >= 2
    assert any("day-of-month" in r for r in result.reasons)


def test_warning_increases_score():
    no_warn = rank("0 9 * * *", _make_valid(warnings=[]), _no_suggestions())
    with_warn = rank("0 9 * * *", _make_valid(warnings=["some warning"]), _no_suggestions())
    assert with_warn.score > no_warn.score


def test_suggestion_increases_score():
    no_sug = rank("0 0 * * *", _make_valid(), _no_suggestions())
    with_sug = rank("0 0 * * *", _make_valid(), _with_suggestions())
    assert with_sug.score > no_sug.score


def test_score_capped_at_ten():
    v = _make_valid(warnings=["w1", "w2", "w3", "w4", "w5"])
    result = rank("* * 1 * 1", v, _with_suggestions())
    assert result.score <= 10


def test_level_moderate_range():
    result = rank("* 9 * * *", _make_valid(), _no_suggestions())
    assert result.level in ("moderate", "complex", "risky")
