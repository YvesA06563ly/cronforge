"""CLI entry point for the `cronforge inspect` sub-command."""

from __future__ import annotations

import argparse
import json
import sys

from cronforge.inspector import inspect, InspectorError


def build_inspect_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: E501
    description = "Inspect each field of a cron expression."
    if parent is not None:
        parser = parent.add_parser("inspect", help=description)
    else:
        parser = argparse.ArgumentParser(prog="cronforge-inspect", description=description)

    parser.add_argument("expression", help="Cron expression in quotes, e.g. '*/15 * * * *'")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser


def _run_inspect(args: argparse.Namespace) -> int:
    try:
        result = inspect(args.expression)
    except InspectorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        payload = {
            "expression": result.expression,
            "fields": [
                {
                    "name": fi.name,
                    "raw": fi.raw,
                    "kind": fi.kind,
                    "values": fi.values,
                    "notes": fi.notes,
                }
                for fi in result.fields
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())

    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_inspect_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_inspect(args))


if __name__ == "__main__":
    main()
