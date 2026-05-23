"""Export cron schedules to various formats (JSON, YAML, TOML-like dict)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from cronforge.parser import CronExpression, CronParseError
from cronforge.humanizer import humanize, HumanizerError
from cronforge.scheduler import CronScheduler


class ExporterError(Exception):
    """Raised when export fails."""


@dataclass
class ExportPayload:
    expression: str
    human_readable: str
    timezone: str
    next_occurrences: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_toml_dict(self) -> dict[str, Any]:
        """Return a dict suitable for embedding in a TOML document."""
        d = self.to_dict()
        d["next_occurrences"] = ", ".join(self.next_occurrences)
        return d


def export(
    expression: str,
    timezone: str = "UTC",
    count: int = 5,
) -> ExportPayload:
    """Build an ExportPayload for the given cron expression.

    Args:
        expression: Standard 5-field cron expression string.
        timezone:   IANA timezone name (default ``"UTC"``).
        count:      Number of upcoming occurrences to include.

    Returns:
        An :class:`ExportPayload` instance.

    Raises:
        ExporterError: If parsing, humanizing, or scheduling fails.
    """
    try:
        parsed = CronExpression.parse(expression)
    except CronParseError as exc:
        raise ExporterError(f"Invalid expression: {exc}") from exc

    try:
        human = humanize(parsed)
    except HumanizerError as exc:
        raise ExporterError(f"Humanize failed: {exc}") from exc

    try:
        scheduler = CronScheduler(expression, timezone=timezone)
        occurrences = [
            dt.isoformat() for dt in scheduler.upcoming(count=count)
        ]
    except Exception as exc:
        raise ExporterError(f"Scheduler error: {exc}") from exc

    return ExportPayload(
        expression=str(parsed),
        human_readable=human,
        timezone=timezone,
        next_occurrences=occurrences,
    )
