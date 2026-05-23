"""Profile cron expressions by analysing execution density over a time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from cronforge.scheduler import CronScheduler, SchedulerError


class ProfilerError(Exception):
    """Raised when profiling fails."""


@dataclass
class ProfileResult:
    expression: str
    timezone: str
    window_hours: int
    total_occurrences: int
    occurrences_per_hour: float
    occurrences_per_day: float
    busiest_hour: int | None  # 0-23
    quietest_hour: int | None  # 0-23
    hour_distribution: dict = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Timezone   : {self.timezone}",
            f"Window     : {self.window_hours}h",
            f"Total runs : {self.total_occurrences}",
            f"Per hour   : {self.occurrences_per_hour:.2f}",
            f"Per day    : {self.occurrences_per_day:.2f}",
        ]
        if self.busiest_hour is not None:
            lines.append(f"Busiest hr : {self.busiest_hour:02d}:00")
        if self.quietest_hour is not None:
            lines.append(f"Quietest hr: {self.quietest_hour:02d}:00")
        return "\n".join(lines)


def profile(
    expression: str,
    timezone: str = "UTC",
    window_hours: int = 24,
) -> ProfileResult:
    """Analyse how often *expression* fires within *window_hours*."""
    if window_hours < 1 or window_hours > 8760:
        raise ProfilerError("window_hours must be between 1 and 8760")

    try:
        scheduler = CronScheduler(expression, timezone=timezone)
        occurrences: List[datetime] = scheduler.upcoming(count=window_hours * 60)
    except SchedulerError as exc:
        raise ProfilerError(str(exc)) from exc

    if not occurrences:
        raise ProfilerError("No occurrences found — expression may be unreachable")

    start = occurrences[0]
    cutoff = start + timedelta(hours=window_hours)
    windowed = [dt for dt in occurrences if dt < cutoff]

    hour_dist: dict[int, int] = {h: 0 for h in range(24)}
    for dt in windowed:
        hour_dist[dt.hour] += 1

    total = len(windowed)
    per_hour = total / window_hours
    per_day = per_hour * 24

    busiest = max(hour_dist, key=lambda h: hour_dist[h]) if total else None
    quietest = min(hour_dist, key=lambda h: hour_dist[h]) if total else None

    return ProfileResult(
        expression=expression,
        timezone=timezone,
        window_hours=window_hours,
        total_occurrences=total,
        occurrences_per_hour=round(per_hour, 4),
        occurrences_per_day=round(per_day, 4),
        busiest_hour=busiest,
        quietest_hour=quietest,
        hour_distribution={str(k): v for k, v in hour_dist.items()},
    )
