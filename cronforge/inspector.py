"""Field-level inspection of a cron expression, reporting type and metadata per field."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from cronforge.parser import CronExpression, CronParseError


class InspectorError(Exception):
    """Raised when inspection cannot be completed."""


@dataclass
class FieldInspection:
    name: str
    raw: str
    kind: str          # wildcard | specific | range | step | list | alias
    values: List[str]  # individual tokens after splitting on ','
    notes: List[str] = field(default_factory=list)


@dataclass
class InspectResult:
    expression: str
    fields: List[FieldInspection]

    def summary(self) -> str:
        lines = [f"Expression : {self.expression}"]
        for fi in self.fields:
            notes = f"  [{', '.join(fi.notes)}]" if fi.notes else ""
            lines.append(f"  {fi.name:<15} {fi.raw:<20} kind={fi.kind}{notes}")
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]

_MONTH_ALIASES = {"jan", "feb", "mar", "apr", "may", "jun",
                  "jul", "aug", "sep", "oct", "nov", "dec"}
_DOW_ALIASES = {"sun", "mon", "tue", "wed", "thu", "fri", "sat"}


def _classify_token(token: str, field_name: str) -> str:
    if token == "*":
        return "wildcard"
    if token.lower() in _MONTH_ALIASES or token.lower() in _DOW_ALIASES:
        return "alias"
    if "/" in token:
        return "step"
    if "-" in token:
        return "range"
    return "specific"


def _inspect_field(name: str, raw: str) -> FieldInspection:
    tokens = raw.split(",")
    if len(tokens) > 1:
        kind = "list"
    else:
        kind = _classify_token(tokens[0], name)

    notes: List[str] = []
    if kind == "step":
        base, step = (tokens[0].split("/") + [""])[:2]
        if step == "1":
            notes.append("step-1 equivalent to wildcard")
    if kind == "list":
        notes.append(f"{len(tokens)} items")

    return FieldInspection(name=name, raw=raw, kind=kind, values=tokens, notes=notes)


def inspect(expression: str) -> InspectResult:
    """Parse *expression* and return a per-field inspection report."""
    try:
        parsed = CronExpression(expression)
    except CronParseError as exc:
        raise InspectorError(str(exc)) from exc

    raw_fields = expression.split()
    if len(raw_fields) != 5:
        raise InspectorError("Expression must have exactly 5 fields.")

    inspections = [
        _inspect_field(name, raw)
        for name, raw in zip(_FIELD_NAMES, raw_fields)
    ]
    return InspectResult(expression=expression, fields=inspections)
