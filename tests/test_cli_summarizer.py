"""Tests for crontab_lint.cli_summarizer."""
import json
import textwrap
from pathlib import Path

import pytest

from crontab_lint.cli_summarizer import run_summary


@pytest.fixture()
def valid_file(tmp_path: Path) -> Path:
    p = tmp_path / "crons.txt"
    p.write_text(textwrap.dedent("""\
        0 9 * * 1-5
        30 6 * * *
        @daily
    """))
    return p


@pytest.fixture()
def mixed_file(tmp_path: Path) -> Path:
    p = tmp_path / "mixed.txt"
    p.write_text(textwrap.dedent("""\
        0 9 * * 1-5
        99 * * * *
    """))
    return p


class _Args:
    def __init__(self, file: Path, as_json: bool = False):
        self.file = file
        self.as_json = as_json


def test_valid_file_returns_zero(valid_file: Path):
    assert run_summary(_Args(valid_file)) == 0


def test_mixed_file_returns_nonzero(mixed_file: Path):
    assert run_summary(_Args(mixed_file)) != 0


def test_missing_file_returns_2(tmp_path: Path):
    missing = tmp_path / "nope.txt"
    assert run_summary(_Args(missing)) == 2


def test_json_output_is_valid(valid_file: Path, capsys):
    run_summary(_Args(valid_file, as_json=True))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "total" in data
    assert "valid" in data
    assert "invalid" in data
    assert "valid_pct" in data


def test_text_output_contains_totals(valid_file: Path, capsys):
    run_summary(_Args(valid_file))
    captured = capsys.readouterr()
    assert "Total" in captured.out
    assert "Valid" in captured.out


def test_invalid_listed_in_text_output(mixed_file: Path, capsys):
    run_summary(_Args(mixed_file))
    captured = capsys.readouterr()
    assert "Invalid expressions" in captured.out
    assert "99 * * * *" in captured.out
