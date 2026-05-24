"""Tests for cronforge.grouper."""

import pytest

from cronforge.grouper import GrouperError, GroupResult, group


EXPRS = [
    "0 9 * * 1",
    "30 9 * * 2",
    "0 12 * * *",
    "15 12 1 * *",
    "* * * * *",
]


def test_returns_group_result():
    result = group(EXPRS, group_by="hour")
    assert isinstance(result, GroupResult)


def test_group_by_hour_keys():
    result = group(EXPRS, group_by="hour")
    assert "9" in result.groups
    assert "12" in result.groups
    assert "*" in result.groups


def test_group_by_hour_counts():
    result = group(EXPRS, group_by="hour")
    assert len(result.groups["9"]) == 2
    assert len(result.groups["12"]) == 2
    assert len(result.groups["*"]) == 1


def test_group_by_minute():
    result = group(EXPRS, group_by="minute")
    assert "0" in result.groups
    assert "30" in result.groups
    assert "15" in result.groups
    assert "*" in result.groups


def test_group_by_dow():
    result = group(EXPRS, group_by="dow")
    assert "1" in result.groups
    assert "2" in result.groups
    assert "*" in result.groups


def test_group_by_field_name_preserved():
    result = group(EXPRS, group_by="month")
    assert result.group_by == "month"


def test_no_ungrouped_for_valid_expressions():
    result = group(EXPRS, group_by="hour")
    assert result.ungrouped == []


def test_invalid_expression_goes_to_ungrouped():
    bad = ["not a cron", "0 9 * * 1"]
    result = group(bad, group_by="hour")
    assert len(result.ungrouped) == 1
    assert "not a cron" in result.ungrouped


def test_invalid_group_by_raises():
    with pytest.raises(GrouperError, match="Invalid group_by field"):
        group(EXPRS, group_by="second")


def test_empty_input_returns_empty_groups():
    result = group([], group_by="hour")
    assert result.groups == {}
    assert result.ungrouped == []


def test_summary_contains_group_by():
    result = group(EXPRS, group_by="hour")
    s = result.summary()
    assert "hour" in s


def test_summary_lists_expressions():
    result = group(["0 9 * * 1", "30 9 * * 2"], group_by="hour")
    s = result.summary()
    assert "0 9 * * 1" in s
    assert "30 9 * * 2" in s


def test_summary_mentions_unparseable():
    result = group(["bad expr"], group_by="minute")
    s = result.summary()
    assert "unparseable" in s
