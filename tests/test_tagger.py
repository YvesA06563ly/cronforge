"""Tests for cronforge.tagger."""

import pytest

from cronforge.tagger import tag, TagResult, TaggerError


def test_returns_tag_result():
    result = tag("* * * * *")
    assert isinstance(result, TagResult)


def test_every_minute_tag():
    result = tag("* * * * *")
    assert "every-minute" in result.tags


def test_high_frequency_step():
    result = tag("*/5 * * * *")
    assert "high-frequency" in result.tags


def test_periodic_step_30():
    result = tag("*/30 * * * *")
    assert "periodic" in result.tags
    assert "high-frequency" not in result.tags


def test_scheduled_hour_tag():
    result = tag("0 9 * * *")
    assert "scheduled-hour" in result.tags


def test_day_restricted_dom():
    result = tag("0 0 1 * *")
    assert "day-restricted" in result.tags


def test_day_restricted_dow():
    result = tag("0 8 * * 1")
    assert "day-restricted" in result.tags


def test_month_restricted():
    result = tag("0 0 1 1 *")
    assert "month-restricted" in result.tags


def test_weekdays_only_range():
    result = tag("0 9 * * 1-5")
    assert "weekdays-only" in result.tags


def test_custom_tag_fallback():
    result = tag("0 9 * * *")
    assert "custom" not in result.tags or "scheduled-hour" in result.tags


def test_summary_contains_expression():
    result = tag("*/15 * * * *")
    assert "*/15 * * * *" in result.summary()


def test_summary_contains_tags():
    result = tag("*/15 * * * *")
    for t in result.tags:
        assert t in result.summary()


def test_invalid_expression_raises():
    with pytest.raises(TaggerError):
        tag("not a cron")


def test_expression_preserved():
    expr = "0 12 * * 1-5"
    result = tag(expr)
    assert result.expression == expr
