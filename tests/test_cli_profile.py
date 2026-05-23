"""Tests for cronforge.cli_profile."""

import json
import pytest

from cronforge.cli_profile import _run_profile, build_profile_parser


@pytest.fixture()
def parser():
    return build_profile_parser()


def _run(parser, argv):
    args = parser.parse_args(argv)
    return _run_profile(args)


def test_text_output_exit_zero(parser, capsys):
    code = _run(parser, ["*/15 * * * *", "--window", "2"])
    assert code == 0


def test_text_output_contains_expression(parser, capsys):
    _run(parser, ["*/15 * * * *", "--window", "2"])
    captured = capsys.readouterr()
    assert "*/15 * * * *" in captured.out


def test_json_output_is_valid(parser, capsys):
    code = _run(parser, ["*/30 * * * *", "--format", "json", "--window", "2"])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "expression" in data
    assert "total_occurrences" in data


def test_json_contains_hour_distribution(parser, capsys):
    _run(parser, ["* * * * *", "--format", "json", "--window", "1"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "hour_distribution" in data
    assert len(data["hour_distribution"]) == 24


def test_invalid_expression_returns_nonzero(parser, capsys):
    code = _run(parser, ["not_valid", "--window", "1"])
    assert code != 0


def test_timezone_flag_accepted(parser, capsys):
    code = _run(parser, ["0 * * * *", "--timezone", "Europe/Paris", "--window", "4"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Europe/Paris" in captured.out
