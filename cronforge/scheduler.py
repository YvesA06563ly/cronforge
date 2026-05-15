"""Timezone-aware scheduling previews for cron expressions."""

from datetime import datetime, timedelta
from typing import Iterator, List, Optional

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # type: ignore

from cronforge.parser import CronExpression, CronParseError


class SchedulerError(Exception):
    """Raised when scheduling preview fails."""


class CronScheduler:
    """Generates upcoming run times for a cron expression in a given timezone."""

    def __init__(self, expression: str, timezone: str = "UTC") -> None:
        self.expression = expression
        try:
            self.tz = ZoneInfo(timezone)
        except (KeyError, ZoneInfoNotFoundError) as exc:
            raise SchedulerError(f"Unknown timezone: {timezone!r}") from exc
        try:
            self._cron = CronExpression.parse(expression)
        except CronParseError as exc:
            raise SchedulerError(f"Invalid cron expression: {exc}") from exc

    def _matches(self, dt: datetime) -> bool:
        """Return True if *dt* matches the cron expression."""
        c = self._cron
        return (
            c.minute.matches(dt.minute)
            and c.hour.matches(dt.hour)
            and c.day.matches(dt.day)
            and c.month.matches(dt.month)
            and c.weekday.matches(dt.weekday() + 1)  # cron: 1=Mon … 7=Sun
        )

    def upcoming(self, count: int = 5, after: Optional[datetime] = None) -> List[datetime]:
        """Return the next *count* scheduled datetimes."""
        if count < 1:
            raise SchedulerError("count must be >= 1")
        start = (after or datetime.now(tz=self.tz)).replace(second=0, microsecond=0)
        start += timedelta(minutes=1)
        results: List[datetime] = []
        candidate = start
        limit = 60 * 24 * 366 * 4  # ~4 years of minutes
        for _ in range(limit):
            if self._matches(candidate):
                results.append(candidate)
                if len(results) == count:
                    break
            candidate += timedelta(minutes=1)
        return results

    def preview(self, count: int = 5, after: Optional[datetime] = None) -> str:
        """Return a human-readable preview of upcoming run times."""
        times = self.upcoming(count=count, after=after)
        lines = [f"Next {len(times)} runs for '{self.expression}' ({self.tz.key}):"]
        for i, dt in enumerate(times, 1):
            lines.append(f"  {i}. {dt.strftime('%Y-%m-%d %H:%M %Z')}")
        return "\n".join(lines)
