"""CLI entry-point for the `cronforge profile` sub-command."""

from __future__ import annotations

import argparse
import json
import sys

from cronforge.profiler import ProfilerError, profile


def build_profile_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: SLF001
    kwargs = dict(
        prog="cronforge profile",
        description="Analyse execution density of a cron expression.",
    )
    parser = parent.add_parser("profile", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("expression", help="Cron expression (quote it!)")
    parser.add_argument(
        "--timezone", "-z", default="UTC", metavar="TZ",
        help="IANA timezone name (default: UTC)",
    )
    parser.add_argument(
        "--window", "-w", type=int, default=24, metavar="HOURS",
        help="Analysis window in hours (default: 24)",
    )
    parser.add_argument(
        "--format", "-f", choices=["text", "json"], default="text",
        dest="fmt", help="Output format (default: text)",
    )
    return parser


def _run_profile(args: argparse.Namespace) -> int:
    try:
        result = profile(args.expression, timezone=args.timezone, window_hours=args.window)
    except ProfilerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.fmt == "json":
        payload = {
            "expression": result.expression,
            "timezone": result.timezone,
            "window_hours": result.window_hours,
            "total_occurrences": result.total_occurrences,
            "occurrences_per_hour": result.occurrences_per_hour,
            "occurrences_per_day": result.occurrences_per_day,
            "busiest_hour": result.busiest_hour,
            "quietest_hour": result.quietest_hour,
            "hour_distribution": result.hour_distribution,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())

    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_profile_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_profile(args))


if __name__ == "__main__":
    main()
