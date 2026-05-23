"""CLI entry point for ranking cron expressions."""

from __future__ import annotations

import argparse
import sys

from cronforge.ranker import RankerError, rank


def build_rank_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronforge-rank",
        description="Score a cron expression by complexity.",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to rank, e.g. '*/15 * * * *'",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON.",
    )
    return parser


def _run_rank(expression: str, as_json: bool) -> int:
    try:
        result = rank(expression)
    except RankerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if as_json:
        import json

        payload = {
            "expression": result.expression,
            "score": result.score,
            "reasons": result.reasons,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())

    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_rank_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_rank(args.expression, args.json))


if __name__ == "__main__":
    main()
