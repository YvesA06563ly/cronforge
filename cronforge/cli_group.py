"""CLI entry point for the cronforge grouper."""

from __future__ import annotations

import argparse
import json
import sys

from cronforge.grouper import GrouperError, group


def build_group_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronforge-group",
        description="Group cron expressions by a shared field.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Cron expressions to group (quote each one).",
    )
    parser.add_argument(
        "--by",
        dest="group_by",
        default="hour",
        choices=["minute", "hour", "dom", "month", "dow"],
        help="Field to group by (default: hour).",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default="text",
        choices=["text", "json"],
        help="Output format (default: text).",
    )
    return parser


def _run_group(args: argparse.Namespace) -> int:
    try:
        result = group(args.expressions, group_by=args.group_by)
    except GrouperError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.fmt == "json":
        payload = {
            "group_by": result.group_by,
            "groups": result.groups,
            "ungrouped": result.ungrouped,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())

    return 0


def main() -> None:  # pragma: no cover
    parser = build_group_parser()
    args = parser.parse_args()
    sys.exit(_run_group(args))


if __name__ == "__main__":  # pragma: no cover
    main()
