"""Tests for cronforge.parser module."""

import pytest
from cronforge.parser import parse, CronParseError


def test_parse_all_wildcards():
    expr = parse("* * * * *")
    assert expr.fields["minute"].values == list(range(0, 60))
    assert expr.fields["hour"].values == list(range(0, 24))
    assert expr.fields["day_of_month"].values == list(range(1, 32))
    assert expr.fields["month"].values == list(range(1, 13))
    assert expr.fields["day_of_week"].values == list(range(0, 7))


def test_parse_specific_values():
    expr = parse("30 9 15 6 1")
    assert expr.fields["minute"].values == [30]
    assert expr.fields["hour"].values == [9]
    assert expr.fields["day_of_month"].values == [15]
    assert expr.fields["month"].values == [6]
    assert expr.fields["day_of_week"].values == [1]


def test_parse_step_expression():
    expr = parse("*/15 * * * *")
    assert expr.fields["minute"].values == [0, 15, 30, 45]


def test_parse_range():
    expr = parse("0 9-17 * * *")
    assert expr.fields["hour"].values == list(range(9, 18))


def test_parse_range_with_step():
    expr = parse("0 0-23/6 * * *")
    assert expr.fields["hour"].values == [0, 6, 12, 18]


def test_parse_comma_list():
    expr = parse("0 8,12,18 * * *")
    assert expr.fields["hour"].values == [8, 12, 18]


def test_parse_month_alias():
    expr = parse("0 0 1 jan *")
    assert expr.fields["month"].values == [1]

    expr = parse("0 0 1 dec *")
    assert expr.fields["month"].values == [12]


def test_parse_dow_alias():
    expr = parse("0 0 * * mon")
    assert expr.fields["day_of_week"].values == [1]

    expr = parse("0 0 * * fri")
    assert expr.fields["day_of_week"].values == [5]


def test_parse_invalid_field_count():
    with pytest.raises(CronParseError, match="Expected 5 fields"):
        parse("* * * *")


def test_parse_out_of_range():
    with pytest.raises(CronParseError, match="out of range"):
        parse("60 * * * *")

    with pytest.raises(CronParseError, match="out of range"):
        parse("* 24 * * *")


def test_parse_invalid_range_order():
    with pytest.raises(CronParseError, match="Invalid range"):
        parse("0 18-9 * * *")


def test_parse_zero_step_raises():
    with pytest.raises(CronParseError, match="Step cannot be zero"):
        parse("*/0 * * * *")


def test_parse_invalid_token():
    with pytest.raises(CronParseError, match="Invalid token"):
        parse("? * * * *")


def test_str_representation():
    raw = "*/5 9-17 * * 1-5"
    expr = parse(raw)
    assert str(expr) == raw
