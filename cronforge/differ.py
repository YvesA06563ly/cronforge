"""Diff two cron expressions and summarize their scheduling differences."""

from dataclasses import dataclass, field
from typing import List

from cronforge.parser import CronExpression, CronParseError
from cronforge.humanizer import humanize


class DifferError(Exception):
    """Raised when diffing fails."""


@dataclass
class DiffResult:
    expr_a: str
    expr_b: str
    human_a: str
    human_b: str
    differences: List[str] = field(default_factory=list)
    identical: bool = False

    def summary(self) -> str:
        if self.identical:
            return f"Expressions are equivalent.\n  Both: {self.human_a}"
        lines = [
            f"A: {self.human_a}",
            f"B: {self.human_b}",
            "Differences:",
        ]
        lines.extend(f"  - {d}" for d in self.differences)
        return "\n".join(lines)


_FIELD_NAMES = ("minute", "hour", "day-of-month", "month", "day-of-week")


def diff(expr_a: str, expr_b: str) -> DiffResult:
    """Compare two cron expressions field by field.

    Args:
        expr_a: First cron expression string.
        expr_b: Second cron expression string.

    Returns:
        A DiffResult describing how the two expressions differ.

    Raises:
        DifferError: If either expression cannot be parsed.
    """
    try:
        parsed_a = CronExpression.parse(expr_a)
    except CronParseError as exc:
        raise DifferError(f"Invalid expression A '{expr_a}': {exc}") from exc

    try:
        parsed_b = CronExpression.parse(expr_b)
    except CronParseError as exc:
        raise DifferError(f"Invalid expression B '{expr_b}': {exc}") from exc

    human_a = humanize(expr_a)
    human_b = humanize(expr_b)

    fields_a = (parsed_a.minute, parsed_a.hour, parsed_a.dom, parsed_a.month, parsed_a.dow)
    fields_b = (parsed_b.minute, parsed_b.hour, parsed_b.dom, parsed_b.month, parsed_b.dow)

    differences: List[str] = []
    for name, fa, fb in zip(_FIELD_NAMES, fields_a, fields_b):
        raw_a = str(fa)
        raw_b = str(fb)
        if raw_a != raw_b:
            differences.append(f"{name}: '{raw_a}' vs '{raw_b}'")

    return DiffResult(
        expr_a=expr_a,
        expr_b=expr_b,
        human_a=human_a,
        human_b=human_b,
        differences=differences,
        identical=len(differences) == 0,
    )
