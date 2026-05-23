"""CLI entry-point for the *tag* sub-command."""

from __future__ import annotations

import argparse
import json
import sys

from cronforge.tagger import tag, TaggerError


def build_tag_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Tag a cron expression with semantic labels."
    if parent is not None:
        parser = parent.add_parser("tag", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="cronforge-tag", description=description)

    parser.add_argument("expression", help="Cron expression to tag (quote it)")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser


def _run_tag(args: argparse.Namespace) -> int:
    try:
        result = tag(args.expression)
    except TaggerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps({"expression": result.expression, "tags": result.tags}, indent=2))
    else:
        print(result.summary())
    return 0


def main() -> None:  # pragma: no cover
    parser = build_tag_parser()
    args = parser.parse_args()
    sys.exit(_run_tag(args))


if __name__ == "__main__":  # pragma: no cover
    main()
