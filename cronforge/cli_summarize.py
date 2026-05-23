"""CLI entry-point for the cronforge summarize sub-command."""

from __future__ import annotations

import argparse
import json
import sys

from cronforge.summarizer import summarize, SummarizerError


def build_summarize_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: E501
    description = "Show a statistical summary of a cron schedule."
    if parent is not None:
        parser = parent.add_parser("summarize", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="cronforge-summarize", description=description)

    parser.add_argument("expression", help="Cron expression (5-field standard)")
    parser.add_argument(
        "--timezone", "-tz",
        default="UTC",
        help="IANA timezone name (default: UTC)",
    )
    parser.add_argument(
        "--sample", "-n",
        type=int,
        default=50,
        dest="sample_size",
        help="Number of occurrences to sample (default: 50, min: 2)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format: text (default) or json",
    )
    return parser


def _run_summarize(args: argparse.Namespace) -> int:
    try:
        result = summarize(
            args.expression,
            timezone=args.timezone,
            sample_size=args.sample_size,
        )
    except SummarizerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.output_format == "json":
        payload = {
            "expression": result.expression,
            "timezone": result.timezone,
            "total_occurrences": result.total_occurrences,
            "average_interval_seconds": round(result.average_interval_seconds, 3),
            "min_interval_seconds": round(result.min_interval_seconds, 3),
            "max_interval_seconds": round(result.max_interval_seconds, 3),
            "occurrences_per_hour": round(result.occurrences_per_hour, 4),
            "occurrences_per_day": round(result.occurrences_per_day, 4),
            "sample_dates": result.sample_dates,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())
        if result.sample_dates:
            print("\nNext occurrences:")
            for date_str in result.sample_dates:
                print(f"  {date_str}")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_summarize_parser()
    args = parser.parse_args()
    sys.exit(_run_summarize(args))


if __name__ == "__main__":  # pragma: no cover
    main()
