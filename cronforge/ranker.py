"""Rank and score cron expressions by complexity and human-friendliness."""

from dataclasses import dataclass, field
from typing import List

from cronforge.parser import CronExpression, CronParseError


class RankerError(Exception):
    """Raised when ranking fails."""


@dataclass
class RankResult:
    expression: str
    score: int  # lower = simpler
    reasons: List[str] = field(default_factory=list)

    def summary(self) -> str:
        label = "simple" if self.score <= 2 else ("moderate" if self.score <= 5 else "complex")
        lines = [f"Expression : {self.expression}", f"Score      : {self.score} ({label})"]
        if self.reasons:
            lines.append("Reasons    :")
            for r in self.reasons:
                lines.append(f"  - {r}")
        return "\n".join(lines)


def _field_complexity(value: str) -> tuple[int, List[str]]:
    """Return (score_delta, reasons) for a single field string."""
    score = 0
    reasons: List[str] = []
    if value == "*":
        return 0, []
    if "," in value:
        count = value.count(",") + 1
        score += count
        reasons.append(f"list with {count} values in field '{value}'")
    if "-" in value and "/" not in value:
        score += 1
        reasons.append(f"range expression in field '{value}'")
    if "/" in value:
        score += 1
        reasons.append(f"step expression in field '{value}'")
    if score == 0:
        score += 1  # specific non-wildcard value
    return score, reasons


def rank(expression: str) -> RankResult:
    """Compute a complexity score for a cron expression."""
    try:
        parsed = CronExpression(expression)
    except CronParseError as exc:
        raise RankerError(f"Cannot rank invalid expression: {exc}") from exc

    fields = [
        parsed.minute,
        parsed.hour,
        parsed.day_of_month,
        parsed.month,
        parsed.day_of_week,
    ]

    total_score = 0
    all_reasons: List[str] = []
    for f in fields:
        delta, reasons = _field_complexity(f)
        total_score += delta
        all_reasons.extend(reasons)

    return RankResult(expression=expression, score=total_score, reasons=all_reasons)
