"""High-level explain helper combining parsing, humanization, and validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .humanizer import humanize, HumanizerError
from .parser import CronExpression, CronParseError
from .validator import ValidationResult, validate


class ExplainError(Exception):
    """Raised when explain cannot produce a result."""


@dataclass
class ExplainResult:
    """Aggregated explanation for a cron expression."""

    expression: str
    human: str
    validation: ValidationResult
    fields: List[str]

    def render(self, *, show_warnings: bool = True) -> str:
        """Render a multi-line explanation suitable for terminal output."""
        lines = [
            f"Expression : {self.expression}",
            f"Meaning    : {self.human}",
            "Fields     :",
        ]
        labels = ["minute", "hour", "day-of-month", "month", "day-of-week"]
        for label, raw in zip(labels, self.fields):
            lines.append(f"  {label:<14} {raw}")
        if show_warnings and self.validation.warnings:
            lines.append("Warnings:")
            for w in self.validation.warnings:
                lines.append(f"  ⚠  {w}")
        return "\n".join(lines)


def explain(expression: str) -> ExplainResult:
    """Return an :class:`ExplainResult` for *expression*.

    Raises
    ------
    ExplainError
        If the expression cannot be parsed or is invalid.
    """
    validation = validate(expression)
    if not validation.valid:
        details = "; ".join(validation.errors)
        raise ExplainError(f"Invalid expression '{expression}': {details}")

    try:
        expr = CronExpression.parse(expression)
    except CronParseError as exc:  # pragma: no cover – already caught above
        raise ExplainError(str(exc)) from exc

    try:
        human = humanize(expression)
    except HumanizerError as exc:
        raise ExplainError(str(exc)) from exc

    raw_fields = [f.raw for f in expr.fields]
    return ExplainResult(
        expression=expression,
        human=human,
        validation=validation,
        fields=raw_fields,
    )
