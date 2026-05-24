"""Tests for cronforge.inspector."""

import pytest
from cronforge.inspector import inspect, InspectResult, FieldInspection, InspectorError


def test_returns_inspect_result():
    result = inspect("* * * * *")
    assert isinstance(result, InspectResult)


def test_expression_preserved():
    result = inspect("0 12 * * 1")
    assert result.expression == "0 12 * * 1"


def test_five_fields_returned():
    result = inspect("* * * * *")
    assert len(result.fields) == 5


def test_field_names_correct():
    result = inspect("* * * * *")
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day-of-month", "month", "day-of-week"]


def test_wildcard_kind():
    result = inspect("* * * * *")
    for fi in result.fields:
        assert fi.kind == "wildcard"


def test_specific_kind():
    result = inspect("0 12 * * *")
    assert result.fields[0].kind == "specific"   # minute = 0
    assert result.fields[1].kind == "specific"   # hour = 12


def test_step_kind():
    result = inspect("*/15 * * * *")
    assert result.fields[0].kind == "step"


def test_range_kind():
    result = inspect("0 9-17 * * *")
    assert result.fields[1].kind == "range"


def test_list_kind():
    result = inspect("0,30 * * * *")
    assert result.fields[0].kind == "list"


def test_list_note_contains_item_count():
    result = inspect("0,15,30,45 * * * *")
    fi = result.fields[0]
    assert any("4 items" in n for n in fi.notes)


def test_alias_kind_month():
    result = inspect("0 0 1 Jan *")
    assert result.fields[3].kind == "alias"


def test_alias_kind_dow():
    result = inspect("0 0 * * Mon")
    assert result.fields[4].kind == "alias"


def test_step_one_note():
    result = inspect("*/1 * * * *")
    fi = result.fields[0]
    assert any("step-1" in n for n in fi.notes)


def test_invalid_expression_raises():
    with pytest.raises(InspectorError):
        inspect("not a cron")


def test_summary_contains_expression():
    result = inspect("0 6 * * *")
    s = result.summary()
    assert "0 6 * * *" in s


def test_summary_contains_field_names():
    result = inspect("0 6 * * *")
    s = result.summary()
    assert "minute" in s
    assert "hour" in s
