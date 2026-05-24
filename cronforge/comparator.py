"""cronforge.comparator — Side-by-side schedule comparison for two cron expressions.

Produces a structured comparison showing next-run alignment, divergence windows,
and a human-readable summary of how two schedules relate to each other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronforge.parser import CronExpression, CronParseError
from cronforge.scheduler import CronScheduler, SchedulerError
from cronforge.humanizer import humanize


class ComparatorError(Exception):
    """Raised when comparison cannot be completed."""


@dataclass
class CompareResult:
    """Holds the result of comparing two cron expressions."""

    expression_a: str
    expression_b: str
    human_a: str
    human_b: str
    timezone: str
    sample_size: int

    # Occurrences unique to each schedule within the sample window
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)

    # Occurrences shared by both schedules (same minute)
    shared: List[str] = field(default_factory=list)

    def overlap_count(self) -> int:
        """Number of shared trigger times."""
        return len(self.shared)

    def divergence_count(self) -> int:
        """Total number of non-overlapping trigger times across both schedules."""
        return len(self.only_in_a) + len(self.only_in_b)

    def overlap_ratio(self) -> float:
        """Fraction of combined unique times that are shared (0.0 – 1.0)."""
        total = self.overlap_count() + self.divergence_count()
        return self.overlap_count() / total if total else 0.0

    def summary(self) -> str:
        """Return a concise human-readable comparison summary."""
        lines = [
            f"Expression A : {self.expression_a}",
            f"  Readable   : {self.human_a}",
            f"Expression B : {self.expression_b}",
            f"  Readable   : {self.human_b}",
            f"Timezone     : {self.timezone}",
            f"Sample size  : {self.sample_size} occurrences each",
            f"Shared times : {self.overlap_count()}",
            f"Only in A    : {len(self.only_in_a)}",
            f"Only in B    : {len(self.only_in_b)}",
            f"Overlap ratio: {self.overlap_ratio():.1%}",
        ]
        return "\n".join(lines)


def compare(
    expr_a: str,
    expr_b: str,
    *,
    timezone: str = "UTC",
    sample_size: int = 20,
    start: Optional[datetime] = None,
) -> CompareResult:
    """Compare two cron expressions over a sample window.

    Parameters
    ----------
    expr_a:
        First cron expression string.
    expr_b:
        Second cron expression string.
    timezone:
        IANA timezone name used for both schedules.
    sample_size:
        Number of upcoming occurrences to collect for each expression.
    start:
        Datetime to begin sampling from (defaults to now in *timezone*).

    Returns
    -------
    CompareResult
        Structured comparison including shared and divergent trigger times.

    Raises
    ------
    ComparatorError
        If either expression is invalid or the scheduler fails.
    """
    try:
        parsed_a = CronExpression.parse(expr_a)
        parsed_b = CronExpression.parse(expr_b)
    except CronParseError as exc:
        raise ComparatorError(f"Parse error: {exc}") from exc

    try:
        human_a = humanize(parsed_a)
        human_b = humanize(parsed_b)
    except Exception as exc:  # noqa: BLE001
        raise ComparatorError(f"Humanizer error: {exc}") from exc

    try:
        scheduler_a = CronScheduler(expr_a, timezone=timezone)
        scheduler_b = CronScheduler(expr_b, timezone=timezone)
        times_a: List[datetime] = scheduler_a.upcoming(n=sample_size, start=start)
        times_b: List[datetime] = scheduler_b.upcoming(n=sample_size, start=start)
    except SchedulerError as exc:
        raise ComparatorError(f"Scheduler error: {exc}") from exc

    # Truncate to minute precision for overlap detection
    def _minute_key(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M")

    set_a = {_minute_key(dt): dt for dt in times_a}
    set_b = {_minute_key(dt): dt for dt in times_b}

    shared_keys = set(set_a) & set(set_b)
    only_a_keys = set(set_a) - shared_keys
    only_b_keys = set(set_b) - shared_keys

    shared = sorted(set_a[k].isoformat() for k in shared_keys)
    only_in_a = sorted(set_a[k].isoformat() for k in only_a_keys)
    only_in_b = sorted(set_b[k].isoformat() for k in only_b_keys)

    return CompareResult(
        expression_a=expr_a,
        expression_b=expr_b,
        human_a=human_a,
        human_b=human_b,
        timezone=timezone,
        sample_size=sample_size,
        shared=shared,
        only_in_a=only_in_a,
        only_in_b=only_in_b,
    )
