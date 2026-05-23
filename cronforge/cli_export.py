"""CLI sub-command: ``cronforge export`` — export a schedule as JSON or dict."""

from __future__ import annotations

import argparse
import sys

from cronforge.exporter import export, ExporterError


def build_export_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the ``export`` sub-command onto *subparsers*."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        "export",
        help="Export a cron schedule as structured data",
    )
    p.add_argument("expression", help="5-field cron expression")
    p.add_argument(
        "--timezone",
        default="UTC",
        metavar="TZ",
        help="IANA timezone name (default: UTC)",
    )
    p.add_argument(
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of upcoming occurrences to include (default: 5)",
    )
    p.add_argument(
        "--format",
        choices=["json", "toml"],
        default="json",
        dest="fmt",
        help="Output format (default: json)",
    )
    p.set_defaults(func=_run_export)


def _run_export(args: argparse.Namespace) -> int:
    """Execute the export sub-command; returns an exit code."""
    try:
        payload = export(
            args.expression,
            timezone=args.timezone,
            count=args.count,
        )
    except ExporterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.fmt == "json":
        print(payload.to_json())
    else:
        # Minimal TOML-like key = value output
        td = payload.to_toml_dict()
        for key, value in td.items():
            print(f'{key} = "{value}"')

    return 0


def main(argv: list[str] | None = None) -> None:
    """Standalone entry-point for the export sub-command."""
    parser = argparse.ArgumentParser(
        prog="cronforge-export",
        description="Export a cron schedule as structured data",
    )
    subparsers = parser.add_subparsers(dest="command")
    build_export_parser(subparsers)

    # Allow calling without the 'export' sub-command keyword for convenience
    args, remaining = parser.parse_known_args(argv)
    if args.command is None:
        # Treat all args as positional for the export command directly
        parser2 = argparse.ArgumentParser(prog="cronforge-export")
        parser2.add_argument("expression")
        parser2.add_argument("--timezone", default="UTC")
        parser2.add_argument("--count", type=int, default=5)
        parser2.add_argument("--format", choices=["json", "toml"], default="json", dest="fmt")
        args2 = parser2.parse_args(argv)
        args2.func = _run_export  # type: ignore[attr-defined]
        sys.exit(_run_export(args2))
    else:
        sys.exit(args.func(args))


if __name__ == "__main__":
    main()
