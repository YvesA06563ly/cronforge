"""Tests for cronforge.linter."""

import pytest

from cronforge.linter import LinterError, LintResult, lint


def test_clean_expression_ok():
    result = lint("0 9 * * 1")
    assert isinstance(result, LintResult)
    assert result.ok()


def test_clean_expression_summary_no_issues():
    result = lint("0 9 * * 1")
    assert "no issues found" in result.summary()


def test_every_minute_produces_warning():
    result = lint("* * * * *")
    assert not result.ok()
    assert any("every minute" in w.lower() for w in result.warnings)


def test_high_frequency_step_hint():
    result = lint("*/2 * * * *")
    assert any("*/2" in h for h in result.hints)


def test_step_5_no_high_frequency_hint():
    result = lint("*/5 * * * *")
    assert not any("*/5" in h for h in result.hints)


def test_dom_and_dow_both_restricted_warning():
    result = lint("0 12 15 * 5")
    assert not result.ok()
    assert any("day-of-month" in w for w in result.warnings)


def test_redundant_wildcard_step_hint_minute():
    result = lint("*/1 * * * *")
    # */1 hint should appear
    assert any("*/1" in h for h in result.hints)


def test_redundant_wildcard_step_hint_hour():
    result = lint("0 */1 * * *")
    assert any("*/1" in h for h in result.hints)


def test_question_mark_hint():
    result = lint("0 9 ? * *")
    assert any("'?'" in h for h in result.hints)


def test_summary_contains_warn_label():
    result = lint("* * * * *")
    assert "[warn]" in result.summary()


def test_summary_contains_hint_label():
    result = lint("*/1 * * * *")
    assert "[hint]" in result.summary()


def test_invalid_expression_raises_linter_error():
    with pytest.raises(LinterError):
        lint("not a cron")


def test_returns_lint_result_type():
    result = lint("30 6 * * *")
    assert isinstance(result, LintResult)


def test_expression_preserved_in_result():
    expr = "15 14 1 * *"
    result = lint(expr)
    assert result.expression == expr
