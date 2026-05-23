"""Tag and categorize cron expressions with semantic labels."""

from dataclasses import dataclass, field
from typing import List

from cronforge.parser import CronExpression, CronParseError


class TaggerError(Exception):
    """Raised when tagging fails."""


@dataclass
class TagResult:
    expression: str
    tags: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if not self.tags:
            return f"{self.expression}: (no tags)"
        return f"{self.expression}: {', '.join(sorted(self.tags))}"


_FREQUENT_MINUTES = {0, 15, 30, 45}


def _infer_tags(expr: CronExpression) -> List[str]:
    tags: List[str] = []

    minute = str(expr.minute)
    hour = str(expr.hour)
    dom = str(expr.day_of_month)
    month = str(expr.month)
    dow = str(expr.day_of_week)

    if minute == "*" and hour == "*" and dom == "*" and month == "*" and dow == "*":
        tags.append("every-minute")
        return tags

    if minute.startswith("*/"):
        interval = int(minute[2:])
        if interval <= 15:
            tags.append("high-frequency")
        else:
            tags.append("periodic")
    elif minute == "*":
        tags.append("high-frequency")

    if hour != "*" and not hour.startswith("*/"):
        tags.append("scheduled-hour")

    if dom != "*" or dow != "*":
        tags.append("day-restricted")

    if month != "*":
        tags.append("month-restricted")

    if dow in ("1-5", "1,2,3,4,5"):
        tags.append("weekdays-only")
    elif dow in ("0,6", "6,0", "0-6"):
        tags.append("daily")

    if not tags:
        tags.append("custom")

    return tags


def tag(expression: str) -> TagResult:
    """Parse *expression* and return a :class:`TagResult` with semantic tags."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        raise TaggerError(f"Invalid cron expression: {exc}") from exc

    tags = _infer_tags(expr)
    return TagResult(expression=expression, tags=tags)
