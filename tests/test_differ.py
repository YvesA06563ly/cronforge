"""Tests for cronforge.differ."""

import pytest

from cronforge.differ import diff, DiffResult, DifferError


def test_identical_expressions_returns_no_differences():
    result = diff("*/15 * * * *", "*/15 * * * *")
    assert result.identical is True
    assert result.differences == []


def test_identical_summary_mentions_equivalent():
    result = diff("0 0 * * *", "0 0 * * *")
    assert "equivalent" in result.summary().lower()


def test_different_minute_field_detected():
    result = diff("0 * * * *", "30 * * * *")
    assert not result.identical
    assert any("minute" in d for d in result.differences)


def test_different_hour_field_detected():
    result = diff("0 6 * * *", "0 9 * * *")
    assert any("hour" in d for d in result.differences)


def test_multiple_field_differences():
    result = diff("0 6 1 * *", "30 9 * * 1")
    assert len(result.differences) >= 3


def test_summary_contains_both_human_descriptions():
    result = diff("0 6 * * *", "0 12 * * *")
    summary = result.summary()
    assert result.human_a in summary
    assert result.human_b in summary


def test_diff_result_stores_original_expressions():
    result = diff("*/5 * * * *", "*/10 * * * *")
    assert result.expr_a == "*/5 * * * *"
    assert result.expr_b == "*/10 * * * *"


def test_invalid_expr_a_raises_differ_error():
    with pytest.raises(DifferError, match="Invalid expression A"):
        diff("99 * * * *", "* * * * *")


def test_invalid_expr_b_raises_differ_error():
    with pytest.raises(DifferError, match="Invalid expression B"):
        diff("* * * * *", "* 25 * * *")


def test_wildcard_vs_specific_dom():
    result = diff("0 0 * * *", "0 0 1 * *")
    assert any("day-of-month" in d for d in result.differences)


def test_step_vs_wildcard_detected():
    result = diff("*/2 * * * *", "* * * * *")
    assert not result.identical
    assert any("minute" in d for d in result.differences)
