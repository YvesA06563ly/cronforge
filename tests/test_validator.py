"""Tests for cronforge.validator."""

import pytest

from cronforge.validator import ValidationResult, validate


def test_valid_expression_returns_true():
    result = validate("*/15 * * * *")
    assert result.valid is True
    assert bool(result) is True


def test_invalid_expression_returns_false():
    result = validate("not a cron")
    assert result.valid is False
    assert result.errors


def test_errors_populated_on_bad_parse():
    result = validate("99 * * * *")
    # minute 99 is out of range
    assert not result.valid
    assert any("minute" in e for e in result.errors)


def test_out_of_range_hour():
    result = validate("0 25 * * *")
    assert not result.valid
    assert any("hour" in e for e in result.errors)


def test_warning_dom_and_dow_both_restricted():
    result = validate("0 12 15 * 1")
    assert result.valid is True
    assert any("day-of-month" in w and "day-of-week" in w for w in result.warnings)


def test_warning_february_high_dom():
    result = validate("0 0 31 2 *")
    assert result.valid is True
    assert any("February" in w for w in result.warnings)


def test_no_warnings_for_simple_expression():
    result = validate("0 9 * * 1-5")
    assert result.valid is True
    assert result.warnings == []


def test_summary_contains_expression():
    result = validate("*/5 * * * *")
    summary = result.summary()
    assert "*/5 * * * *" in summary
    assert "yes" in summary


def test_summary_contains_errors():
    result = validate("bad expr")
    summary = result.summary()
    assert "no" in summary
    assert "Errors" in summary


def test_validation_result_bool_false():
    r = ValidationResult(expression="x", valid=False)
    assert not r


def test_validation_result_bool_true():
    r = ValidationResult(expression="* * * * *", valid=True)
    assert r


def test_every_minute_is_valid():
    assert validate("* * * * *").valid


def test_step_expression_is_valid():
    assert validate("0 */6 * * *").valid
