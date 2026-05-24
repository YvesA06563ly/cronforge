"""Snapshot a cron expression's upcoming schedule into a portable record."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from cronforge.humanizer import humanize
from cronforge.parser import CronExpression, CronParseError
from cronforge.scheduler import CronScheduler, SchedulerError


class SnapshottingError(Exception):
    """Raised when snapshot generation fails."""


@dataclass
class Snapshot:
    expression: str
    timezone: str
    human_readable: str
    captured_at: str
    occurrences: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Timezone   : {self.timezone}",
            f"Readable   : {self.human_readable}",
            f"Captured   : {self.captured_at}",
            f"Occurrences: {len(self.occurrences)}",
        ]
        for i, ts in enumerate(self.occurrences, 1):
            lines.append(f"  [{i:>2}] {ts}")
        return "\n".join(lines)


def snapshot(
    expression: str,
    *,
    timezone: str = "UTC",
    count: int = 5,
    now: datetime | None = None,
) -> Snapshot:
    """Capture a snapshot of the next *count* occurrences for *expression*."""
    if count < 1 or count > 100:
        raise SnapshottingError("count must be between 1 and 100")

    try:
        parsed = CronExpression.parse(expression)
    except CronParseError as exc:
        raise SnapshottingError(f"Invalid expression: {exc}") from exc

    try:
        human = humanize(parsed)
    except Exception:  # noqa: BLE001
        human = "(unable to describe)"

    try:
        scheduler = CronScheduler(expression, timezone=timezone)
        upcoming = scheduler.upcoming(count=count, now=now)
    except SchedulerError as exc:
        raise SnapshottingError(f"Scheduler error: {exc}") from exc

    import zoneinfo

    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except Exception as exc:
        raise SnapshottingError(f"Unknown timezone '{timezone}': {exc}") from exc

    captured_at = datetime.now(tz=tz).isoformat()

    return Snapshot(
        expression=expression,
        timezone=timezone,
        human_readable=human,
        captured_at=captured_at,
        occurrences=[dt.isoformat() for dt in upcoming],
    )
