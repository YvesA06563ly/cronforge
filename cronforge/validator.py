"""Cron expression validator with detailed diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, CronParseError


class ValidatorError(Exception):
    """Raised when validation encounters an unrecoverable error."""


@dataclass
class ValidationResult:
    """Result of validating a cron expression."""

    expression: str
    valid: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:  # noqa: D105
        return self.valid

    def summary(self) -> str:
        """Return a human-readable summary of the validation result."""
        lines = [f"Expression : {self.expression}"]
        lines.append(f"Valid      : {'yes' if self.valid else 'no'}")
        if self.errors:
            lines.append("Errors:")
            for e in self.errors:
                lines.append(f"  - {e}")
        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        return "\n".join(lines)


# Reasonable upper bounds for each field index
_FIELD_LIMITS = [
    ("minute", 0, 59),
    ("hour", 0, 23),
    ("day-of-month", 1, 31),
    ("month", 1, 12),
    ("day-of-week", 0, 7),
]


def _check_reachable(expr: CronExpression) -> List[str]:
    """Return warnings for combinations that never fire."""
    warnings: List[str] = []
    dom_raw = expr.fields[2].raw
    dow_raw = expr.fields[4].raw
    if dom_raw != "*" and dow_raw != "*":
        warnings.append(
            "Both day-of-month and day-of-week are restricted; "
            "the schedule fires when EITHER condition matches (may be surprising)."
        )
    month_values = expr.fields[3].values
    dom_values = expr.fields[2].values
    if 2 in month_values and any(v > 29 for v in dom_values):
        warnings.append(
            "Day-of-month includes values >29 but month includes February; "
            "those dates will never fire in February."
        )
    return warnings


def validate(expression: str) -> ValidationResult:
    """Validate *expression* and return a :class:`ValidationResult`."""
    result = ValidationResult(expression=expression, valid=False)
    try:
        expr = CronExpression.parse(expression)
    except CronParseError as exc:
        result.errors.append(str(exc))
        return result

    for idx, (name, lo, hi) in enumerate(_FIELD_LIMITS):
        for val in expr.fields[idx].values:
            if not (lo <= val <= hi):
                result.errors.append(
                    f"Field '{name}' contains value {val} outside allowed range [{lo}, {hi}]."
                )

    if not result.errors:
        result.valid = True
        result.warnings.extend(_check_reachable(expr))

    return result
