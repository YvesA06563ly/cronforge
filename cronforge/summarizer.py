"""Summarizer module: produces a concise statistical summary of a cron schedule."""

from dataclasses import dataclass, field
from typing import List

from cronforge.parser import CronExpression, CronParseError
from cronforge.scheduler import CronScheduler, SchedulerError


class SummarizerError(Exception):
    """Raised when summarization fails."""


@dataclass
class ScheduleSummary:
    expression: str
    timezone: str
    total_occurrences: int
    average_interval_seconds: float
    min_interval_seconds: float
    max_interval_seconds: float
    occurrences_per_hour: float
    occurrences_per_day: float
    sample_dates: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Expression : {self.expression}",
            f"Timezone   : {self.timezone}",
            f"Sampled    : {self.total_occurrences} occurrences",
            f"Avg interval : {self.average_interval_seconds:.1f}s",
            f"Min interval : {self.min_interval_seconds:.1f}s",
            f"Max interval : {self.max_interval_seconds:.1f}s",
            f"Per hour   : {self.occurrences_per_hour:.2f}",
            f"Per day    : {self.occurrences_per_day:.2f}",
        ]
        return "\n".join(lines)


def summarize(
    expression: str,
    timezone: str = "UTC",
    sample_size: int = 50,
) -> ScheduleSummary:
    """Analyse *sample_size* upcoming occurrences and return a ScheduleSummary."""
    if sample_size < 2:
        raise SummarizerError("sample_size must be at least 2")

    try:
        parsed = CronExpression.parse(expression)
    except CronParseError as exc:
        raise SummarizerError(f"Invalid expression: {exc}") from exc

    try:
        scheduler = CronScheduler(parsed, timezone=timezone)
        dates = scheduler.upcoming(n=sample_size)
    except SchedulerError as exc:
        raise SummarizerError(f"Scheduler error: {exc}") from exc

    if len(dates) < 2:
        raise SummarizerError("Not enough occurrences to compute intervals")

    intervals = [
        (dates[i + 1] - dates[i]).total_seconds()
        for i in range(len(dates) - 1)
    ]

    avg_interval = sum(intervals) / len(intervals)
    min_interval = min(intervals)
    max_interval = max(intervals)
    per_hour = 3600.0 / avg_interval if avg_interval > 0 else 0.0
    per_day = 86400.0 / avg_interval if avg_interval > 0 else 0.0

    sample_dates = [d.isoformat() for d in dates[:5]]

    return ScheduleSummary(
        expression=expression,
        timezone=timezone,
        total_occurrences=len(dates),
        average_interval_seconds=avg_interval,
        min_interval_seconds=min_interval,
        max_interval_seconds=max_interval,
        occurrences_per_hour=per_hour,
        occurrences_per_day=per_day,
        sample_dates=sample_dates,
    )
