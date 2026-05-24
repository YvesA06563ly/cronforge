"""Formats upcoming schedule previews as tables or plain text."""

from datetime import datetime
from typing import Literal

OutputFormat = Literal["plain", "table", "iso"]


class FormatterError(Exception):
    """Raised when formatting fails."""


def _format_single(dt: datetime, fmt: OutputFormat, index: int | None = None) -> str:
    """Format a single datetime according to the chosen output format."""
    prefix = f"{index + 1:>3}. " if index is not None else ""

    if fmt == "iso":
        return prefix + dt.isoformat()

    if fmt == "table":
        tz_name = dt.tzname() or "UTC"
        return (
            f"{prefix}{dt.strftime('%Y-%m-%d'):12} "
            f"{dt.strftime('%H:%M:%S'):10} "
            f"{tz_name}"
        )

    # plain
    return prefix + dt.strftime("%A, %B %d %Y at %H:%M:%S %Z").strip()


def format_schedule(
    datetimes: list[datetime],
    fmt: OutputFormat = "plain",
    title: str | None = None,
) -> str:
    """Format a list of datetimes into a human-readable schedule string."""
    if not datetimes:
        raise FormatterError("No datetimes provided to format.")

    lines: list[str] = []

    if title:
        lines.append(title)
        lines.append("-" * len(title))

    if fmt == "table":
        header = f"{'#':>3}  {'Date':12} {'Time':10} Timezone"
        lines.append(header)
        lines.append("-" * len(header))

    for i, dt in enumerate(datetimes):
        lines.append(_format_single(dt, fmt, index=i))

    return "\n".join(lines)


def format_next(dt: datetime, fmt: OutputFormat = "plain") -> str:
    """Format a single next-run datetime."""
    return _format_single(dt, fmt)


def format_countdown(dt: datetime, now: datetime | None = None) -> str:
    """Return a human-readable countdown string from now until *dt*.

    Args:
        dt: The future datetime to count down to.
        now: The reference point in time. Defaults to ``datetime.now()``
             (or ``datetime.now(dt.tzinfo)`` when *dt* is timezone-aware).

    Returns:
        A string such as ``"in 2 days, 3 hours, 15 minutes"``.

    Raises:
        FormatterError: If *dt* is not in the future relative to *now*.
    """
    if now is None:
        now = datetime.now(dt.tzinfo)

    delta = dt - now
    total_seconds = int(delta.total_seconds())

    if total_seconds < 0:
        raise FormatterError("Countdown datetime is in the past.")

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return "in " + ", ".join(parts)
