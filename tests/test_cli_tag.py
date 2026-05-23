"""Tests for cronforge.cli_tag."""

import json

import pytest

from cronforge.cli_tag import build_tag_parser, _run_tag


@pytest.fixture()
def parser():
    return build_tag_parser()


def _run(parser, argv):
    args = parser.parse_args(argv)
    return _run_tag(args)


def test_text_output_exit_zero(parser, capsys):
    rc = _run(parser, ["*/15 * * * *"])
    assert rc == 0


def test_text_output_contains_expression(parser, capsys):
    _run(parser, ["*/15 * * * *"])
    captured = capsys.readouterr()
    assert "*/15 * * * *" in captured.out


def test_json_output_is_valid(parser, capsys):
    _run(parser, ["--format", "json", "0 9 * * 1-5"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "expression" in data
    assert "tags" in data
    assert isinstance(data["tags"], list)


def test_json_expression_matches(parser, capsys):
    _run(parser, ["--format", "json", "0 9 * * 1-5"])
    data = json.loads(capsys.readouterr().out)
    assert data["expression"] == "0 9 * * 1-5"


def test_invalid_expression_returns_nonzero(parser, capsys):
    rc = _run(parser, ["bad expression here"])
    assert rc == 1


def test_invalid_expression_prints_to_stderr(parser, capsys):
    _run(parser, ["bad expression here"])
    captured = capsys.readouterr()
    assert "Error" in captured.err
