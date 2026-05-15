"""Tests for cronforge.scheduler module."""

from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

import pytest

from cronforge.scheduler import CronScheduler, SchedulerError


ANCHOR_UTC = datetime(2024, 1, 15, 12, 0, tzinfo=ZoneInfo("UTC"))


def test_upcoming_returns_correct_count():
    scheduler = CronScheduler("*/15 * * * *", timezone="UTC")
    results = scheduler.upcoming(count=4, after=ANCHOR_UTC)
    assert len(results) == 4


def test_upcoming_every_15_minutes():
    scheduler = CronScheduler("*/15 * * * *", timezone="UTC")
    results = scheduler.upcoming(count=4, after=ANCHOR_UTC)
    minutes = [dt.minute for dt in results]
    assert minutes == [15, 30, 45, 0]


def test_upcoming_specific_hour_and_minute():
    scheduler = CronScheduler("30 9 * * *", timezone="UTC")
    results = scheduler.upcoming(count=3, after=ANCHOR_UTC)
    for dt in results:
        assert dt.hour == 9
        assert dt.minute == 30


def test_upcoming_respects_timezone():
    scheduler = CronScheduler("0 0 * * *", timezone="America/New_York")
    results = scheduler.upcoming(count=1, after=datetime(2024, 1, 15, 0, 0, tzinfo=ZoneInfo("America/New_York")))
    assert results[0].hour == 0
    assert results[0].minute == 0
    assert str(results[0].tzinfo) == "America/New_York"


def test_invalid_timezone_raises():
    with pytest.raises(SchedulerError, match="Unknown timezone"):
        CronScheduler("* * * * *", timezone="Mars/Olympus")


def test_invalid_expression_raises():
    with pytest.raises(SchedulerError, match="Invalid cron expression"):
        CronScheduler("99 99 99 99 99")


def test_count_less_than_one_raises():
    scheduler = CronScheduler("* * * * *", timezone="UTC")
    with pytest.raises(SchedulerError, match="count must be >= 1"):
        scheduler.upcoming(count=0)


def test_preview_contains_expression_and_timezone():
    scheduler = CronScheduler("0 8 * * 1", timezone="Europe/London")
    output = scheduler.preview(count=2, after=ANCHOR_UTC)
    assert "0 8 * * 1" in output
    assert "Europe/London" in output


def test_preview_line_count():
    scheduler = CronScheduler("0 12 * * *", timezone="UTC")
    output = scheduler.preview(count=3, after=ANCHOR_UTC)
    lines = output.strip().splitlines()
    # header + 3 result lines
    assert len(lines) == 4
