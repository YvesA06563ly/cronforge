"""Simple CLI for cronforge scheduling previews."""

import argparse
import sys
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

from cronforge.scheduler import CronScheduler, SchedulerError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronforge",
        description="Human-readable cron expression builder and scheduler preview.",
    )
    p.add_argument("expression", help="Cron expression (quote it!), e.g. '*/5 * * * *'")
    p.add_argument(
        "-n", "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of upcoming runs to display (default: 5)",
    )
    p.add_argument(
        "-z", "--timezone",
        default="UTC",
        metavar="TZ",
        help="IANA timezone name (default: UTC)",
    )
    p.add_argument(
        "--after",
        default=None,
        metavar="DATETIME",
        help="Start datetime in ISO format, e.g. 2024-06-01T09:00 (default: now)",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    after: datetime | None = None
    if args.after:
        try:
            naive = datetime.fromisoformat(args.after)
            after = naive.replace(tzinfo=ZoneInfo(args.timezone))
        except ValueError as exc:
            print(f"error: invalid --after datetime: {exc}", file=sys.stderr)
            return 1

    try:
        scheduler = CronScheduler(args.expression, timezone=args.timezone)
        print(scheduler.preview(count=args.count, after=after))
    except SchedulerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
