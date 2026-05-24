"""Annotate a cron expression with inline field-level descriptions."""

from dataclasses import dataclass, field
from typing import Dict

from cronforge.parser import CronExpression, CronParseError
from cronforge.humanizer import _describe_field


class AnnotatorError(Exception):
    """Raised when annotation fails."""


_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


@dataclass
class AnnotateResult:
    expression: str
    annotations: Dict[str, str]
    annotated_line: str

    def summary(self) -> str:
        parts = [f"Expression : {self.expression}", "Fields:"]
        for name, desc in self.annotations.items():
            parts.append(f"  {name:<14} -> {desc}")
        parts.append(f"Inline     : {self.annotated_line}")
        return "\n".join(parts)


def annotate(expression: str) -> AnnotateResult:
    """Return per-field human descriptions and an annotated inline string."""
    try:
        expr = CronExpression.parse(expression)
    except CronParseError as exc:
        raise AnnotatorError(str(exc)) from exc

    raw_fields = expression.split()
    if len(raw_fields) != 5:
        raise AnnotatorError(
            f"Expected 5 fields, got {len(raw_fields)}: {expression!r}"
        )

    field_values = [
        expr.minute,
        expr.hour,
        expr.day_of_month,
        expr.month,
        expr.day_of_week,
    ]

    annotations: Dict[str, str] = {}
    inline_parts = []
    for name, raw, fv in zip(_FIELD_NAMES, raw_fields, field_values):
        desc = _describe_field(name, fv)
        annotations[name] = desc
        inline_parts.append(f"{raw}({desc})")

    annotated_line = " ".join(inline_parts)
    return AnnotateResult(
        expression=expression,
        annotations=annotations,
        annotated_line=annotated_line,
    )
