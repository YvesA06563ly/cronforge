"""CLI entry-point for the annotate sub-command."""

from __future__ import annotations

import argparse
import json
import sys

from cronforge.annotator import annotate, AnnotatorError


def build_annotate_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # noqa: E501
    description = "Annotate each field of a cron expression with a human-readable label."
    if parent is not None:
        parser = parent.add_parser("annotate", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="cronforge-annotate", description=description)

    parser.add_argument("expression", help="Cron expression to annotate (quote it)")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser


def _run_annotate(args: argparse.Namespace) -> int:
    try:
        result = annotate(args.expression)
    except AnnotatorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        payload = {
            "expression": result.expression,
            "annotations": result.annotations,
            "annotated_line": result.annotated_line,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())

    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_annotate_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_annotate(args))


if __name__ == "__main__":  # pragma: no cover
    main()
