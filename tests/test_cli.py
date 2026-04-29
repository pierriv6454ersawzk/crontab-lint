"""Tests for the crontab-lint CLI."""

import textwrap
from pathlib import Path

import pytest

from crontab_lint.cli import main


def test_valid_expression_prints_ok(capsys):
    rc = main(["*/5 * * * *"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK" in out


def test_valid_expression_no_explain(capsys):
    rc = main(["--no-explain", "0 12 * * 1"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK: 0 12 * * 1" in out
    # explanation line should not appear
    assert "At" not in out and "minute" not in out.lower() or "OK" in out


def test_invalid_expression_returns_nonzero(capsys):
    rc = main(["99 * * * *"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "INVALID" in out
    assert "error" in out


def test_no_args_prints_help(capsys):
    rc = main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "usage" in out.lower() or "crontab-lint" in out


def test_file_with_valid_entries(tmp_path, capsys):
    crontab = tmp_path / "crontab"
    crontab.write_text(textwrap.dedent("""\
        # daily backup
        0 2 * * *
        */15 * * * *
    """))
    rc = main(["-f", str(crontab)])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.count("OK") == 2


def test_file_with_invalid_entry(tmp_path, capsys):
    crontab = tmp_path / "crontab"
    crontab.write_text("0 25 * * *\n")
    rc = main(["-f", str(crontab)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "INVALID" in out


def test_file_not_found(capsys):
    rc = main(["-f", "/nonexistent/path/crontab"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "cannot open" in err


def test_file_skips_comments_and_blank_lines(tmp_path, capsys):
    crontab = tmp_path / "crontab"
    crontab.write_text("# comment\n\n0 0 * * *\n")
    rc = main(["-f", str(crontab)])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.count("OK") == 1
