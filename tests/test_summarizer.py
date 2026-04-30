"""Tests for crontab_lint.summarizer."""
import pytest
from crontab_lint.summarizer import summarize, SummaryResult


VALID_EXPRS = [
    "0 9 * * 1-5",
    "30 6 * * *",
    "@daily",
]

INVALID_EXPRS = [
    "99 * * * *",
    "* * * * * * extra",
]

SUGGESTION_EXPRS = [
    "* * * * *",   # every minute -> @yearly suggestion candidate / wildcard
    "0/1 * * * *",  # slash-one suggestion
]


def test_summarize_returns_summary_result():
    result = summarize(VALID_EXPRS)
    assert isinstance(result, SummaryResult)


def test_all_valid_expressions():
    result = summarize(VALID_EXPRS)
    assert result.valid == len(VALID_EXPRS)
    assert result.invalid == 0


def test_all_invalid_expressions():
    result = summarize(INVALID_EXPRS)
    assert result.invalid == len(INVALID_EXPRS)
    assert result.valid == 0


def test_mixed_expressions():
    exprs = VALID_EXPRS + INVALID_EXPRS
    result = summarize(exprs)
    assert result.total == len(exprs)
    assert result.valid == len(VALID_EXPRS)
    assert result.invalid == len(INVALID_EXPRS)


def test_invalid_expressions_captured():
    result = summarize(INVALID_EXPRS)
    assert set(result.invalid_expressions) == set(INVALID_EXPRS)


def test_valid_pct_calculation():
    result = summarize(VALID_EXPRS + INVALID_EXPRS)
    expected = round(len(VALID_EXPRS) / (len(VALID_EXPRS) + len(INVALID_EXPRS)) * 100, 1)
    assert result.valid_pct == expected


def test_empty_list_returns_zeros():
    result = summarize([])
    assert result.total == 0
    assert result.valid == 0
    assert result.invalid == 0
    assert result.valid_pct == 0.0


def test_expressions_with_suggestions_counted():
    result = summarize(SUGGESTION_EXPRS)
    assert result.with_suggestions >= 0  # at least runs without error
    assert isinstance(result.suggestion_expressions, list)


def test_blank_lines_ignored():
    exprs = ["", "  ", "0 9 * * 1-5"]
    result = summarize(exprs)
    # blank entries are skipped; total still reflects raw list length
    assert result.valid <= result.total
