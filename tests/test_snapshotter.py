"""Tests for cronforge.snapshotter."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cronforge.snapshotter import Snapshot, SnapshottingError, snapshot


_NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_returns_snapshot_instance():
    result = snapshot("* * * * *", timezone="UTC", count=3, now=_NOW)
    assert isinstance(result, Snapshot)


def test_expression_preserved():
    result = snapshot("0 9 * * 1", timezone="UTC", count=2, now=_NOW)
    assert result.expression == "0 9 * * 1"


def test_timezone_preserved():
    result = snapshot("*/15 * * * *", timezone="America/New_York", count=2, now=_NOW)
    assert result.timezone == "America/New_York"


def test_occurrence_count_matches_requested():
    result = snapshot("* * * * *", timezone="UTC", count=5, now=_NOW)
    assert len(result.occurrences) == 5


def test_occurrences_are_iso_strings():
    result = snapshot("*/30 * * * *", timezone="UTC", count=3, now=_NOW)
    for occ in result.occurrences:
        # Should parse without error
        datetime.fromisoformat(occ)


def test_occurrences_are_ordered():
    result = snapshot("*/10 * * * *", timezone="UTC", count=4, now=_NOW)
    parsed = [datetime.fromisoformat(o) for o in result.occurrences]
    assert parsed == sorted(parsed)


def test_human_readable_non_empty():
    result = snapshot("0 0 * * *", timezone="UTC", count=2, now=_NOW)
    assert isinstance(result.human_readable, str)
    assert len(result.human_readable) > 0


def test_captured_at_is_iso_string():
    result = snapshot("* * * * *", timezone="UTC", count=1, now=_NOW)
    datetime.fromisoformat(result.captured_at)


def test_summary_contains_expression():
    result = snapshot("5 4 * * 0", timezone="UTC", count=2, now=_NOW)
    assert "5 4 * * 0" in result.summary()


def test_summary_contains_occurrence_lines():
    result = snapshot("* * * * *", timezone="UTC", count=3, now=_NOW)
    s = result.summary()
    assert "[ 1]" in s
    assert "[ 3]" in s


def test_invalid_expression_raises():
    with pytest.raises(SnapshottingError, match="Invalid expression"):
        snapshot("invalid cron expr", timezone="UTC", count=3, now=_NOW)


def test_invalid_timezone_raises():
    with pytest.raises(SnapshottingError, match="Unknown timezone"):
        snapshot("* * * * *", timezone="Not/AZone", count=3, now=_NOW)


def test_count_zero_raises():
    with pytest.raises(SnapshottingError, match="count must be"):
        snapshot("* * * * *", timezone="UTC", count=0, now=_NOW)


def test_count_over_limit_raises():
    with pytest.raises(SnapshottingError, match="count must be"):
        snapshot("* * * * *", timezone="UTC", count=101, now=_NOW)
