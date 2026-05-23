"""Cron expression linter that reports style and best-practice warnings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, CronParseError


class LinterError(Exception):
    """Raised when the linter encounters an unrecoverable error."""


@dataclass
class LintResult:
    expression: str
    warnings: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.ok() and not self.hints:
            return f"{self.expression}: no issues found"
        lines = [f"{self.expression}:"]
        for w in self.warnings:
            lines.append(f"  [warn]  {w}")
        for h in self.hints:
            lines.append(f"  [hint]  {h}")
        return "\n".join(lines)


def _check_dom_dow_conflict(expr: CronExpression, result: LintResult) -> None:
    dom_restricted = expr.dom.raw != "*"
    dow_restricted = expr.dow.raw != "*"
    if dom_restricted and dow_restricted:
        result.warnings.append(
            "Both day-of-month and day-of-week are restricted; "
            "most cron implementations use OR semantics which may cause unexpected runs."
        )


def _check_high_frequency(expr: CronExpression, result: LintResult) -> None:
    raw = expr.minute.raw
    if raw == "*":
        result.warnings.append(
            "Expression runs every minute — consider whether this frequency is intentional."
        )
    elif raw.startswith("*/"):
        try:
            step = int(raw[2:])
            if step < 5:
                result.hints.append(
                    f"Minute step */{step} triggers very frequently; "
                    "ensure the scheduled job completes within the interval."
                )
        except ValueError:
            pass


def _check_non_standard_characters(expr: CronExpression, result: LintResult) -> None:
    for name, f in [
        ("minute", expr.minute),
        ("hour", expr.hour),
        ("dom", expr.dom),
        ("month", expr.month),
        ("dow", expr.dow),
    ]:
        if "?" in f.raw:
            result.hints.append(
                f"Field '{name}' uses '?' which is not standard POSIX cron; "
                "it may not be supported by all schedulers."
            )


def _check_redundant_wildcard_step(expr: CronExpression, result: LintResult) -> None:
    for name, f in [("minute", expr.minute), ("hour", expr.hour)]:
        if f.raw == "*/1":
            result.hints.append(
                f"Field '{name}': '*/1' is equivalent to '*'; prefer the simpler form."
            )


def lint(expression: str) -> LintResult:
    """Lint *expression* and return a :class:`LintResult`."""
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        raise LinterError(str(exc)) from exc

    result = LintResult(expression=expression)
    _check_dom_dow_conflict(expr, result)
    _check_high_frequency(expr, result)
    _check_non_standard_characters(expr, result)
    _check_redundant_wildcard_step(expr, result)
    return result
