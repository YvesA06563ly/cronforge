"""Tests for the schedule formatter."""

import pytest
from datetime import datetime, timezone, timedelta
from cronforge.formatter import format_schedule, format_next, FormatterError

UTC = timezone.utc
EST = timezone(timedelta(hours=-5), name="EST")

SAMPLE = [
    datetime(2024, 6, 1, 9, 0, 0, tzinfo=UTC),
    datetime(2024, 6, 1, 9, 15, 0, tzinfo=UTC),
    datetime(2024, 6, 1, 9, 30, 0, tzinfo=UTC),
]


def test_plain_format_contains_weekday():
    result = format_schedule(SAMPLE, fmt="plain")
    assert "Saturday" in result


def test_plain_format_line_count():
    result = format_schedule(SAMPLE, fmt="plain")
    assert len(result.strip().splitlines()) == 3


def test_table_format_has_header():
    result = format_schedule(SAMPLE, fmt="table")
    assert "Date" in result
    assert "Time" in result
    assert "Timezone" in result


def test_table_format_line_count():
    result = format_schedule(SAMPLE, fmt="table")
    lines = result.strip().splitlines()
    # header + separator + 3 entries
    assert len(lines) == 5


def test_iso_format():
    result = format_schedule(SAMPLE, fmt="iso")
    assert "2024-06-01T09:00:00" in result


def test_with_title():
    result = format_schedule(SAMPLE, fmt="plain", title="My Schedule")
    assert result.startswith("My Schedule")
    assert "---" in result


def test_empty_list_raises_error():
    with pytest.raises(FormatterError):
        format_schedule([], fmt="plain")


def test_format_next_plain():
    dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
    result = format_next(dt, fmt="plain")
    assert "Monday" in result
    assert "January" in result


def test_format_next_iso():
    dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
    result = format_next(dt, fmt="iso")
    assert "2024-01-15T12:00:00" in result


def test_timezone_shown_in_table():
    dt = datetime(2024, 6, 1, 9, 0, 0, tzinfo=EST)
    result = format_schedule([dt], fmt="table")
    assert "EST" in result
