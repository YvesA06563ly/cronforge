"""Tests for cronforge.recommender."""

import pytest

from cronforge.recommender import RecommendResult, RecommenderError, recommend


def test_returns_recommend_result():
    result = recommend("* * * * *")
    assert isinstance(result, RecommendResult)


def test_expression_preserved():
    expr = "0 0 * * *"
    result = recommend(expr)
    assert result.expression == expr


def test_already_minimal_no_suggestions():
    result = recommend("30 6 * * 1")
    assert result.suggestions == []


def test_step_one_minute_simplified():
    result = recommend("*/1 * * * *")
    assert any("*" in s for s in result.suggestions)


def test_step_one_produces_note():
    result = recommend("*/1 * * * *")
    assert any("minute" in n for n in result.notes)


def test_daily_alias_suggested():
    result = recommend("0 0 * * *")
    assert "@daily" in result.suggestions


def test_hourly_alias_suggested():
    result = recommend("0 * * * *")
    assert "@hourly" in result.suggestions


def test_every_minute_alias_suggested():
    result = recommend("* * * * *")
    assert "@every_minute" in result.suggestions


def test_weekly_alias_suggested():
    result = recommend("0 0 * * 0")
    assert "@weekly" in result.suggestions


def test_monthly_alias_suggested():
    result = recommend("0 0 1 * *")
    assert "@monthly" in result.suggestions


def test_yearly_alias_suggested():
    result = recommend("0 0 1 1 *")
    assert "@yearly" in result.suggestions


def test_invalid_expression_raises():
    with pytest.raises(RecommenderError):
        recommend("not a cron")


def test_summary_no_suggestions():
    result = recommend("15 10 * * 1")
    assert "no simpler" in result.summary()


def test_summary_with_suggestions():
    result = recommend("0 0 * * *")
    assert "->" in result.summary()


def test_step_one_hour_simplified():
    result = recommend("0 */1 * * *")
    # */1 on hour should simplify to *
    assert any("hour" in n for n in result.notes)
