"""CLI entry-point for the cronforge linter."""

from __future__ import annotations

import argparse
import json
import sys

from .linter import LinterError, lint


def build_lint_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[name-defined]
    kwargs = dict(
        prog="cronforge lint",
        description="Lint a cron expression for style and best-practice issues.",
    )
    if parent is not None:
        parser = parent.add_parser("lint", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("expression", help="Cron expression to lint (quote it).")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return parser


def _run_lint(args: argparse.Namespace) -> int:
    try:
        result = lint(args.expression)
    except LinterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        payload = {
            "expression": result.expression,
            "ok": result.ok(),
            "warnings": result.warnings,
            "hints": result.hints,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())

    return 0 if result.ok() else 1


def main(argv: list[str] | None = None) -> None:
    parser = build_lint_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_lint(args))


if __name__ == "__main__":  # pragma: no cover
    main()
