"""Tests for cronforge.profiler."""

import pytest

from cronforge.profiler import ProfileResult, ProfilerError, profile


def test_returns_profile_result():
    result = profile("*/15 * * * *", timezone="UTC", window_hours=2)
    assert isinstance(result, ProfileResult)


def test_expression_preserved():
    expr = "*/30 * * * *"
    result = profile(expr, timezone="UTC", window_hours=2)
    assert result.expression == expr


def test_timezone_preserved():
    result = profile("0 * * * *", timezone="America/New_York", window_hours=4)
    assert result.timezone == "America/New_York"


def test_every_minute_total_occurrences():
    result = profile("* * * * *", timezone="UTC", window_hours=1)
    assert result.total_occurrences == 60


def test_every_15_minutes_occurrences_per_hour():
    result = profile("*/15 * * * *", timezone="UTC", window_hours=4)
    assert result.occurrences_per_hour == pytest.approx(4.0, rel=0.05)


def test_every_hour_occurrences_per_day():
    result = profile("0 * * * *", timezone="UTC", window_hours=48)
    assert result.occurrences_per_day == pytest.approx(24.0, rel=0.05)


def test_hour_distribution_has_24_keys():
    result = profile("*/10 * * * *", timezone="UTC", window_hours=24)
    assert len(result.hour_distribution) == 24


def test_busiest_and_quietest_hour_present_for_uniform_schedule():
    result = profile("* * * * *", timezone="UTC", window_hours=2)
    assert result.busiest_hour is not None
    assert result.quietest_hour is not None


def test_invalid_window_too_small_raises():
    with pytest.raises(ProfilerError, match="window_hours"):
        profile("* * * * *", window_hours=0)


def test_invalid_window_too_large_raises():
    with pytest.raises(ProfilerError, match="window_hours"):
        profile("* * * * *", window_hours=9000)


def test_invalid_expression_raises():
    with pytest.raises(ProfilerError):
        profile("not_a_cron", window_hours=1)


def test_summary_contains_expression():
    result = profile("*/5 * * * *", timezone="UTC", window_hours=1)
    assert "*/5 * * * *" in result.summary()


def test_summary_contains_timezone():
    result = profile("0 12 * * *", timezone="Europe/London", window_hours=24)
    assert "Europe/London" in result.summary()
