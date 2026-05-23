"""Tests for cronforge.exporter."""

from __future__ import annotations

import json

import pytest

from cronforge.exporter import export, ExporterError, ExportPayload


def test_export_returns_payload():
    payload = export("*/15 * * * *", timezone="UTC", count=3)
    assert isinstance(payload, ExportPayload)


def test_export_expression_preserved():
    payload = export("0 9 * * 1-5", timezone="UTC", count=2)
    assert payload.expression == "0 9 * * 1-5"


def test_export_human_readable_non_empty():
    payload = export("0 0 * * *", timezone="UTC", count=1)
    assert isinstance(payload.human_readable, str)
    assert len(payload.human_readable) > 0


def test_export_correct_occurrence_count():
    payload = export("*/5 * * * *", timezone="UTC", count=4)
    assert len(payload.next_occurrences) == 4


def test_export_occurrences_are_iso_strings():
    payload = export("0 12 * * *", timezone="UTC", count=3)
    for occ in payload.next_occurrences:
        # Basic ISO-8601 sanity: contains 'T' separator
        assert "T" in occ


def test_export_timezone_stored():
    payload = export("0 8 * * *", timezone="America/New_York", count=1)
    assert payload.timezone == "America/New_York"


def test_to_dict_has_expected_keys():
    payload = export("*/30 * * * *", timezone="UTC", count=2)
    d = payload.to_dict()
    assert set(d.keys()) == {
        "expression",
        "human_readable",
        "timezone",
        "next_occurrences",
    }


def test_to_json_is_valid_json():
    payload = export("0 0 1 * *", timezone="UTC", count=2)
    raw = payload.to_json()
    parsed = json.loads(raw)
    assert parsed["expression"] == "0 0 1 * *"


def test_to_toml_dict_occurrences_is_string():
    payload = export("*/10 * * * *", timezone="UTC", count=3)
    td = payload.to_toml_dict()
    assert isinstance(td["next_occurrences"], str)
    assert "," in td["next_occurrences"] or len(payload.next_occurrences) == 1


def test_invalid_expression_raises_exporter_error():
    with pytest.raises(ExporterError, match="Invalid expression"):
        export("not a cron", timezone="UTC", count=1)


def test_invalid_timezone_raises_exporter_error():
    with pytest.raises(ExporterError):
        export("* * * * *", timezone="Not/ATimezone", count=1)
