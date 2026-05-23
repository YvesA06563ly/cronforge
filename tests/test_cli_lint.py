"""Tests for cronforge.cli_lint."""

import json
import pytest

from cronforge.cli_lint import build_lint_parser, _run_lint


@pytest.fixture()
def parser():
    return build_lint_parser()


def _run(parser, argv):
    args = parser.parse_args(argv)
    return _run_lint(args)


def test_text_output_exit_zero_clean(parser):
    code = _run(parser, ["0 9 * * 1"])
    assert code == 0


def test_text_output_exit_one_with_warnings(parser):
    code = _run(parser, ["* * * * *"])
    assert code == 1


def test_text_output_contains_expression(parser, capsys):
    _run(parser, ["0 9 * * 1"])
    captured = capsys.readouterr()
    assert "0 9 * * 1" in captured.out


def test_json_output_is_valid(parser, capsys):
    _run(parser, ["0 9 * * 1", "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "expression" in data
    assert "ok" in data
    assert "warnings" in data
    assert "hints" in data


def test_json_ok_true_for_clean(parser, capsys):
    _run(parser, ["0 9 * * 1", "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True


def test_json_ok_false_for_every_minute(parser, capsys):
    _run(parser, ["* * * * *", "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is False
    assert len(data["warnings"]) > 0


def test_invalid_expression_returns_exit_code_2(parser, capsys):
    code = _run(parser, ["not_a_cron"])
    assert code == 2
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()
