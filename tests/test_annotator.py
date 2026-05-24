"""Tests for cronforge.annotator."""

import pytest

from cronforge.annotator import annotate, AnnotateResult, AnnotatorError


def test_returns_annotate_result():
    result = annotate("* * * * *")
    assert isinstance(result, AnnotateResult)


def test_expression_preserved():
    result = annotate("0 9 * * 1")
    assert result.expression == "0 9 * * 1"


def test_annotations_has_all_five_fields():
    result = annotate("*/15 * * * *")
    expected_keys = {"minute", "hour", "day_of_month", "month", "day_of_week"}
    assert set(result.annotations.keys()) == expected_keys


def test_annotations_non_empty_strings():
    result = annotate("0 0 1 1 *")
    for key, value in result.annotations.items():
        assert isinstance(value, str) and len(value) > 0, f"Empty annotation for {key}"


def test_annotated_line_contains_raw_fields():
    expr = "30 6 * * 1-5"
    result = annotate(expr)
    for raw in expr.split():
        assert raw in result.annotated_line


def test_annotated_line_has_five_segments():
    result = annotate("0 12 * * *")
    # Each segment is "raw(desc)"; split by space gives 5 parts
    segments = result.annotated_line.split(" ")
    assert len(segments) == 5


def test_summary_contains_expression():
    result = annotate("0 0 * * *")
    assert "0 0 * * *" in result.summary()


def test_summary_contains_field_names():
    result = annotate("* * * * *")
    summary = result.summary()
    for name in ("minute", "hour", "day_of_month", "month", "day_of_week"):
        assert name in summary


def test_invalid_expression_raises_annotator_error():
    with pytest.raises(AnnotatorError):
        annotate("not a cron")


def test_too_few_fields_raises_annotator_error():
    with pytest.raises(AnnotatorError):
        annotate("* * *")


def test_step_expression_annotation():
    result = annotate("*/5 * * * *")
    assert "5" in result.annotations["minute"] or "every" in result.annotations["minute"].lower()


def test_specific_dow_annotation():
    result = annotate("0 9 * * 1")
    ann = result.annotations["day_of_week"].lower()
    assert "monday" in ann or "1" in ann
