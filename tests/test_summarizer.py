"""Tests for cronforge.summarizer."""

import pytest

from cronforge.summarizer import summarize, ScheduleSummary, SummarizerError


def test_returns_schedule_summary():
    result = summarize("*/15 * * * *", timezone="UTC", sample_size=10)
    assert isinstance(result, ScheduleSummary)


def test_expression_preserved():
    expr = "*/15 * * * *"
    result = summarize(expr, timezone="UTC", sample_size=10)
    assert result.expression == expr


def test_timezone_preserved():
    result = summarize("0 * * * *", timezone="America/New_York", sample_size=10)
    assert result.timezone == "America/New_York"


def test_occurrence_count_matches_sample_size():
    result = summarize("*/5 * * * *", timezone="UTC", sample_size=20)
    assert result.total_occurrences == 20


def test_every_15_minutes_avg_interval():
    result = summarize("*/15 * * * *", timezone="UTC", sample_size=10)
    assert abs(result.average_interval_seconds - 900.0) < 1.0


def test_every_hour_avg_interval():
    result = summarize("0 * * * *", timezone="UTC", sample_size=10)
    assert abs(result.average_interval_seconds - 3600.0) < 1.0


def test_min_max_interval_equal_for_uniform_schedule():
    result = summarize("*/10 * * * *", timezone="UTC", sample_size=10)
    assert abs(result.min_interval_seconds - result.max_interval_seconds) < 1.0


def test_occurrences_per_hour_every_minute():
    result = summarize("* * * * *", timezone="UTC", sample_size=10)
    assert abs(result.occurrences_per_hour - 60.0) < 0.1


def test_occurrences_per_day_every_hour():
    result = summarize("0 * * * *", timezone="UTC", sample_size=10)
    assert abs(result.occurrences_per_day - 24.0) < 0.1


def test_sample_dates_non_empty():
    result = summarize("*/30 * * * *", timezone="UTC", sample_size=10)
    assert len(result.sample_dates) > 0


def test_sample_dates_are_iso_strings():
    result = summarize("*/30 * * * *", timezone="UTC", sample_size=10)
    for date_str in result.sample_dates:
        assert "T" in date_str


def test_sample_dates_capped_at_five():
    result = summarize("* * * * *", timezone="UTC", sample_size=50)
    assert len(result.sample_dates) <= 5


def test_invalid_expression_raises():
    with pytest.raises(SummarizerError, match="Invalid expression"):
        summarize("invalid cron", timezone="UTC")


def test_invalid_timezone_raises():
    with pytest.raises((SummarizerError, Exception)):
        summarize("* * * * *", timezone="Not/ATimezone")


def test_sample_size_less_than_two_raises():
    with pytest.raises(SummarizerError, match="sample_size"):
        summarize("* * * * *", timezone="UTC", sample_size=1)


def test_summary_string_contains_expression():
    result = summarize("*/15 * * * *", timezone="UTC", sample_size=10)
    text = result.summary()
    assert "*/15 * * * *" in text


def test_summary_string_contains_timezone():
    result = summarize("0 * * * *", timezone="Europe/London", sample_size=10)
    text = result.summary()
    assert "Europe/London" in text
