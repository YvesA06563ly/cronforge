"""Normalize cron expressions to a canonical form."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from cronforge.parser import CronExpression, CronParseError


class NormalizerError(Exception):
    """Raised when normalization fails."""


@dataclass
class NormalizeResult:
    original: str
    normalized: str
    changes: List[str]

    def summary(self) -> str:
        if not self.changes:
            return f"'{self.original}' is already in canonical form."
        lines = [f"Normalized '{self.original}' -> '{self.normalized}':"] + [
            f"  - {c}" for c in self.changes
        ]
        return "\n".join(lines)


def _normalize_field(raw: str, aliases: dict[str, str]) -> tuple[str, list[str]]:
    """Return (normalized_field, list_of_change_descriptions)."""
    changes: list[str] = []
    parts = raw.split(",")
    normalized_parts: list[str] = []

    for part in parts:
        original_part = part
        # Resolve named aliases (e.g. JAN->1, MON->1)
        upper = part.upper()
        if upper in aliases:
            part = aliases[upper]
            changes.append(f"Replaced alias '{original_part}' with '{part}'")
        # Normalize */1 -> *
        if part == "*/1":
            part = "*"
            changes.append("Replaced '*/1' with '*'")
        # Normalize ranges where start == end (e.g. 5-5 -> 5)
        if "-" in part and "/" not in part:
            lo, _, hi = part.partition("-")
            if lo.isdigit() and hi.isdigit() and lo == hi:
                part = lo
                changes.append(f"Collapsed range '{original_part}' to '{part}'")
        normalized_parts.append(part)

    return ",".join(normalized_parts), changes


_MONTH_ALIASES = {
    "JAN": "1", "FEB": "2", "MAR": "3", "APR": "4",
    "MAY": "5", "JUN": "6", "JUL": "7", "AUG": "8",
    "SEP": "9", "OCT": "10", "NOV": "11", "DEC": "12",
}

_DOW_ALIASES = {
    "SUN": "0", "MON": "1", "TUE": "2", "WED": "3",
    "THU": "4", "FRI": "5", "SAT": "6",
}

_FIELD_ALIASES = [
    {},           # minute
    {},           # hour
    {},           # day-of-month
    _MONTH_ALIASES,  # month
    _DOW_ALIASES,    # day-of-week
]


def normalize(expression: str) -> NormalizeResult:
    """Parse and normalize *expression* to its canonical string form."""
    try:
        CronExpression(expression)  # validate first
    except CronParseError as exc:
        raise NormalizerError(f"Cannot normalize invalid expression: {exc}") from exc

    fields = expression.split()
    if len(fields) != 5:
        raise NormalizerError("Expression must have exactly 5 fields.")

    all_changes: list[str] = []
    normalized_fields: list[str] = []

    for raw, aliases in zip(fields, _FIELD_ALIASES):
        norm, changes = _normalize_field(raw, aliases)
        normalized_fields.append(norm)
        all_changes.extend(changes)

    normalized = " ".join(normalized_fields)
    return NormalizeResult(
        original=expression,
        normalized=normalized,
        changes=all_changes,
    )
