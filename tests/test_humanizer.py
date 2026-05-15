"""Tests for the cron expression humanizer."""

import pytest
from cronforge.humanizer import humanize, HumanizerError


def test_every_minute():
    assert humanize("* * * * *") == "every minute"


def test_every_15_minutes():
    result = humanize("*/15 * * * *")
    assert result == "every 15 minutes"


def test_specific_hour_and_minute():
    result = humanize("30 9 * * *")
    assert "minute 30" in result
    assert "hour 9" in result


def test_with_day_of_month():
    result = humanize("0 0 1 * *")
    assert "day" in result
    assert "1" in result


def test_with_month():
    result = humanize("0 0 * 6 *")
    assert "June" in result


def test_with_day_of_week():
    result = humanize("0 9 * * 1")
    assert "Monday" in result


def test_with_range_of_months():
    result = humanize("0 0 * 6-8 *")
    assert "June" in result
    assert "August" in result


def test_with_multiple_days_of_week():
    result = humanize("0 9 * * 1,3,5")
    assert "Monday" in result
    assert "Wednesday" in result
    assert "Friday" in result


def test_step_in_range():
    result = humanize("0 8-18/2 * * *")
    assert "every 2" in result
    assert "8" in result
    assert "18" in result


def test_invalid_expression_raises_humanizer_error():
    with pytest.raises(HumanizerError):
        humanize("invalid expression")


def test_invalid_field_raises_humanizer_error():
    with pytest.raises(HumanizerError):
        humanize("99 * * * *")


def test_full_complex_expression():
    result = humanize("30 8 15 12 5")
    assert "30" in result
    assert "8" in result
    assert "15" in result
    assert "December" in result
    assert "Friday" in result
