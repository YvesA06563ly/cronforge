"""Tests for cronforge.normalizer."""

import pytest

from cronforge.normalizer import NormalizeResult, NormalizerError, normalize


def test_returns_normalize_result():
    result = normalize("* * * * *")
    assert isinstance(result, NormalizeResult)


def test_already_canonical_has_no_changes():
    result = normalize("* * * * *")
    assert result.changes == []
    assert result.normalized == "* * * * *"


def test_step_one_normalized_to_wildcard():
    result = normalize("*/1 * * * *")
    assert result.normalized == "* * * * *"
    assert any("*/1" in c for c in result.changes)


def test_month_alias_replaced():
    result = normalize("0 0 1 JAN *")
    assert "1" in result.normalized.split()[3]
    assert any("JAN" in c for c in result.changes)


def test_dow_alias_replaced():
    result = normalize("0 9 * * MON")
    normalized_dow = result.normalized.split()[4]
    assert normalized_dow == "1"
    assert any("MON" in c for c in result.changes)


def test_collapsed_single_value_range():
    result = normalize("5-5 * * * *")
    assert result.normalized.split()[0] == "5"
    assert any("5-5" in c for c in result.changes)


def test_no_collapse_for_real_range():
    result = normalize("1-5 * * * *")
    assert result.normalized.split()[0] == "1-5"


def test_multiple_changes_in_one_expression():
    result = normalize("*/1 */1 * JAN MON")
    norm_fields = result.normalized.split()
    assert norm_fields[0] == "*"
    assert norm_fields[1] == "*"
    assert norm_fields[3] == "1"
    assert norm_fields[4] == "1"
    assert len(result.changes) >= 4


def test_original_preserved():
    expr = "0 12 * * FRI"
    result = normalize(expr)
    assert result.original == expr


def test_summary_no_changes():
    result = normalize("0 12 * * 5")
    assert "canonical" in result.summary()


def test_summary_with_changes():
    result = normalize("*/1 * * JAN *")
    s = result.summary()
    assert "->" in s
    assert "Normalized" in s


def test_invalid_expression_raises():
    with pytest.raises(NormalizerError, match="Cannot normalize"):
        normalize("99 * * * *")


def test_wrong_field_count_raises():
    with pytest.raises(NormalizerError):
        normalize("* * *")


def test_comma_list_with_alias():
    result = normalize("0 0 * JAN,FEB *")
    month_field = result.normalized.split()[3]
    assert month_field == "1,2"
