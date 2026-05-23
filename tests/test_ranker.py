"""Tests for cronforge.ranker."""

import pytest

from cronforge.ranker import RankerError, RankResult, rank


def test_all_wildcards_lowest_score():
    result = rank("* * * * *")
    assert isinstance(result, RankResult)
    assert result.score == 0


def test_specific_minute_adds_score():
    result = rank("30 * * * *")
    assert result.score >= 1


def test_step_expression_adds_score():
    result = rank("*/15 * * * *")
    assert result.score >= 1
    assert any("step" in r for r in result.reasons)


def test_list_expression_adds_score():
    result = rank("0,15,30,45 * * * *")
    assert result.score >= 4
    assert any("list" in r for r in result.reasons)


def test_range_expression_adds_score():
    result = rank("0 9-17 * * 1-5")
    assert result.score >= 2
    assert any("range" in r for r in result.reasons)


def test_complex_expression_higher_than_simple():
    simple = rank("0 * * * *")
    complex_ = rank("0,30 9-17 * 1,6 1-5")
    assert complex_.score > simple.score


def test_invalid_expression_raises_ranker_error():
    with pytest.raises(RankerError, match="Cannot rank invalid expression"):
        rank("not a cron")


def test_summary_contains_expression():
    result = rank("*/5 * * * *")
    summary = result.summary()
    assert "*/5 * * * *" in summary


def test_summary_label_simple():
    result = rank("* * * * *")
    assert "simple" in result.summary()


def test_summary_label_complex():
    result = rank("1,2,3,4,5,6 * * * *")
    assert "complex" in result.summary() or "moderate" in result.summary()


def test_reasons_empty_for_all_wildcards():
    result = rank("* * * * *")
    assert result.reasons == []


def test_reasons_non_empty_for_mixed_expression():
    result = rank("*/10 8 * * 1,5")
    assert len(result.reasons) > 0
