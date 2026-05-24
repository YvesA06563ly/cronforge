"""CLI entry point for the cronforge comparator module.

Allows users to compare two cron expressions and view overlap,
divergence, and similarity statistics from the command line.
"""

from __future__ import annotations

import argparse
import json
import sys

from cronforge.comparator import compare, ComparatorError


def build_comparator_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the compare subcommand."""
    parser = argparse.ArgumentParser(
        prog="cronforge-compare",
        description="Compare two cron expressions for overlap and divergence.",
    )
    parser.add_argument(
        "expression_a",
        metavar="EXPR_A",
        help="First cron expression (e.g. '*/15 * * * *').",
    )
    parser.add_argument(
        "expression_b",
        metavar="EXPR_B",
        help="Second cron expression (e.g. '0 * * * *').",
    )
    parser.add_argument(
        "--timezone",
        "-tz",
        default="UTC",
        metavar="TZ",
        help="IANA timezone name for scheduling previews (default: UTC).",
    )
    parser.add_argument(
        "--sample-size",
        "-n",
        type=int,
        default=100,
        metavar="N",
        help="Number of upcoming occurrences to sample per expression (default: 100).",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format: 'text' (default) or 'json'.",
    )
    return parser


def _run_compare(args: argparse.Namespace) -> int:
    """Execute the compare command and write results to stdout.

    Returns the process exit code (0 = success, 1 = error).
    """
    try:
        result = compare(
            args.expression_a,
            args.expression_b,
            timezone=args.timezone,
            sample_size=args.sample_size,
        )
    except ComparatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        payload = {
            "expression_a": result.expression_a,
            "expression_b": result.expression_b,
            "timezone": result.timezone,
            "sample_size": result.sample_size,
            "overlap_count": result.overlap_count,
            "divergence_count": result.divergence_count,
            "overlap_ratio": result.overlap_ratio,
            "summary": result.summary(),
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"Expression A : {result.expression_a}")
        print(f"Expression B : {result.expression_b}")
        print(f"Timezone     : {result.timezone}")
        print(f"Sample size  : {result.sample_size}")
        print(f"Overlap      : {result.overlap_count} occurrence(s)")
        print(f"Divergence   : {result.divergence_count} occurrence(s)")
        print(f"Overlap ratio: {result.overlap_ratio:.2%}")
        print()
        print(result.summary())

    return 0


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the cronforge-compare CLI."""
    parser = build_comparator_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_compare(args))


if __name__ == "__main__":
    main()
