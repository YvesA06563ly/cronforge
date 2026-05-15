"""High-level explain API combining humanizer, scheduler, and formatter."""

from datetime import datetime
from typing import Literal

from cronforge.humanizer import humanize, HumanizerError
from cronforge.scheduler import CronScheduler, SchedulerError
from cronforge.formatter import format_schedule, OutputFormat


class ExplainError(Exception):
    """Raised when explain fails."""


def explain(
    expression: str,
    count: int = 5,
    timezone: str = "UTC",
    fmt: OutputFormat = "plain",
    start: datetime | None = None,
) -> str:
    """
    Explain a cron expression with a human-readable description
    and a preview of upcoming run times.

    Args:
        expression: A valid cron expression string.
        count: Number of upcoming occurrences to preview.
        timezone: IANA timezone name for scheduling.
        fmt: Output format — 'plain', 'table', or 'iso'.
        start: Optional start datetime for the schedule preview.

    Returns:
        A formatted string with description and upcoming runs.

    Raises:
        ExplainError: If the expression or timezone is invalid.
    """
    try:
        description = humanize(expression)
    except HumanizerError as e:
        raise ExplainError(str(e)) from e

    try:
        scheduler = CronScheduler(expression, timezone=timezone)
        upcoming = scheduler.upcoming(count=count, start=start)
    except SchedulerError as e:
        raise ExplainError(str(e)) from e

    title = f"Expression : {expression}"
    subtitle = f"Description: {description}"
    preview_title = f"Next {count} runs ({timezone})"

    schedule_block = format_schedule(upcoming, fmt=fmt, title=preview_title)

    return "\n".join([title, subtitle, "", schedule_block])
