"""Tests for cronforge.merger module."""

import pytest

from cronforge.merger import merge, MergeResult, MergerError


def test_identical_expressions_no_unified_fields():
    result = merge("0 9 * * 1", "0 9 * * 1")
    assert isinstance(result, MergeResult)
    assert result.merged == "0 9 * * 1"
    assert result.fields_unified == []


def test_different_minute_fields_unified():
    result = merge("0 9 * * *", "30 9 * * *")
    assert "minute" in result.fields_unified
    assert "0" in result.merged
    assert "30" in result.merged


def test_wildcard_takes_precedence_over_specific():
    result = merge("* 9 * * *", "30 9 * * *")
    parts = result.merged.split()
    assert parts[0] == "*"
    assert "minute" in result.fields_unified


def test_different_hour_fields_unified():
    result = merge("0 8 * * *", "0 17 * * *")
    assert "hour" in result.fields_unified
    parts = result.merged.split()
    assert "8" in parts[1] and "17" in parts[1]


def test_multiple_differing_fields():
    result = merge("0 8 1 * *", "0 17 15 * *")
    assert "hour" in result.fields_unified
    assert "dom" in result.fields_unified
    assert len(result.fields_unified) == 2


def test_merged_expression_is_valid_string():
    result = merge("*/15 * * * *", "*/15 * * * *")
    parts = result.merged.split()
    assert len(parts) == 5


def test_human_readable_is_non_empty():
    result = merge("0 9 * * *", "0 10 * * *")
    assert isinstance(result.human_readable, str)
    assert len(result.human_readable) > 0


def test_summary_contains_both_expressions():
    result = merge("0 9 * * *", "0 10 * * *")
    summary = result.summary()
    assert "0 9 * * *" in summary
    assert "0 10 * * *" in summary


def test_summary_mentions_unified_fields():
    result = merge("0 8 * * *", "0 17 * * *")
    assert "hour" in result.summary()


def test_invalid_expression_a_raises_merger_error():
    with pytest.raises(MergerError, match="Invalid expression A"):
        merge("99 * * * *", "0 9 * * *")


def test_invalid_expression_b_raises_merger_error():
    with pytest.raises(MergerError, match="Invalid expression B"):
        merge("0 9 * * *", "* * * * 9")


def test_combined_values_deduplicated():
    result = merge("0,30 9 * * *", "30,45 9 * * *")
    parts = result.merged.split()
    minute_values = parts[0].split(",")
    assert len(minute_values) == len(set(minute_values))
