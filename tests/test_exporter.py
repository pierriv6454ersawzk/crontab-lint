"""Tests for crontab_lint.exporter."""
import csv
import io
import json

import pytest

from crontab_lint.exporter import ExportRow, export, export_csv, export_json, _build_row
from crontab_lint.validator import validate
from crontab_lint.normalizer import normalize


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_row() -> ExportRow:
    return ExportRow(
        expression="0 9 * * 1",
        valid=True,
        normalized=None,
        warnings=[],
        errors=[],
    )


@pytest.fixture
def invalid_row() -> ExportRow:
    return ExportRow(
        expression="99 * * * *",
        valid=False,
        normalized=None,
        warnings=[],
        errors=["minute value 99 out of range"],
    )


# ---------------------------------------------------------------------------
# _build_row
# ---------------------------------------------------------------------------

def test_build_row_valid_no_norm():
    vr = validate("0 9 * * 1")
    row = _build_row("0 9 * * 1", vr, None)
    assert row.valid is True
    assert row.normalized is None


def test_build_row_alias_sets_normalized():
    vr = validate("@daily")
    nr = normalize("@daily")
    row = _build_row("@daily", vr, nr)
    assert row.valid is True
    assert row.normalized == "0 0 * * *"


# ---------------------------------------------------------------------------
# export_json
# ---------------------------------------------------------------------------

def test_export_json_returns_string(valid_row):
    result = export_json([valid_row])
    assert isinstance(result, str)


def test_export_json_structure(valid_row, invalid_row):
    data = json.loads(export_json([valid_row, invalid_row]))
    assert len(data) == 2
    assert data[0]["expression"] == "0 9 * * 1"
    assert data[0]["valid"] is True
    assert data[1]["valid"] is False
    assert "minute value 99 out of range" in data[1]["errors"]


# ---------------------------------------------------------------------------
# export_csv
# ---------------------------------------------------------------------------

def test_export_csv_returns_string(valid_row):
    result = export_csv([valid_row])
    assert isinstance(result, str)


def test_export_csv_has_header(valid_row):
    result = export_csv([valid_row])
    reader = csv.DictReader(io.StringIO(result))
    assert set(reader.fieldnames or []) >= {"expression", "valid", "normalized", "warnings", "errors"}


def test_export_csv_row_count(valid_row, invalid_row):
    result = export_csv([valid_row, invalid_row])
    rows = list(csv.DictReader(io.StringIO(result)))
    assert len(rows) == 2


# ---------------------------------------------------------------------------
# export (high-level)
# ---------------------------------------------------------------------------

def test_export_default_is_json():
    result = export(["* * * * *"])
    data = json.loads(result)
    assert data[0]["expression"] == "* * * * *"


def test_export_csv_format():
    result = export(["0 0 * * *"], fmt="csv")
    rows = list(csv.DictReader(io.StringIO(result)))
    assert rows[0]["expression"] == "0 0 * * *"


def test_export_invalid_expression_marked():
    result = export(["99 * * * *"])
    data = json.loads(result)
    assert data[0]["valid"] is False
