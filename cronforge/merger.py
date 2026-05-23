"""Merge two cron expressions into a unified schedule description."""

from dataclasses import dataclass
from typing import List

from cronforge.parser import CronExpression, CronParseError
from cronforge.humanizer import humanize


class MergerError(Exception):
    """Raised when merging cron expressions fails."""


@dataclass
class MergeResult:
    expression_a: str
    expression_b: str
    merged: str
    human_readable: str
    fields_unified: List[str]

    def summary(self) -> str:
        unified = ", ".join(self.fields_unified) if self.fields_unified else "none"
        return (
            f"Merged '{self.expression_a}' + '{self.expression_b}' "
            f"→ '{self.merged}' (unified fields: {unified})"
        )


def _merge_field(a: str, b: str) -> tuple[str, bool]:
    """Merge two individual cron fields. Returns (merged_value, was_unified)."""
    if a == b:
        return a, False
    if a == "*" or b == "*":
        return "*", True
    # Combine specific values, removing duplicates and sorting
    parts_a = set(a.split(","))
    parts_b = set(b.split(","))
    combined = sorted(parts_a | parts_b, key=lambda x: int(x) if x.isdigit() else 0)
    return ",".join(combined), True


def merge(expr_a: str, expr_b: str) -> MergeResult:
    """Merge two cron expressions into a single combined expression.

    Fields that differ are merged by combining their values. Wildcard
    fields take precedence over specific values.

    Args:
        expr_a: First cron expression string.
        expr_b: Second cron expression string.

    Returns:
        MergeResult with the merged expression and metadata.

    Raises:
        MergerError: If either expression cannot be parsed.
    """
    try:
        parsed_a = CronExpression(expr_a)
    except CronParseError as exc:
        raise MergerError(f"Invalid expression A '{expr_a}': {exc}") from exc

    try:
        parsed_b = CronExpression(expr_b)
    except CronParseError as exc:
        raise MergerError(f"Invalid expression B '{expr_b}': {exc}") from exc

    field_names = ["minute", "hour", "dom", "month", "dow"]
    fields_a = [parsed_a.minute, parsed_a.hour, parsed_a.dom, parsed_a.month, parsed_a.dow]
    fields_b = [parsed_b.minute, parsed_b.hour, parsed_b.dom, parsed_b.month, parsed_b.dow]

    merged_parts: List[str] = []
    unified_fields: List[str] = []

    for name, fa, fb in zip(field_names, fields_a, fields_b):
        merged_val, was_unified = _merge_field(str(fa), str(fb))
        merged_parts.append(merged_val)
        if was_unified:
            unified_fields.append(name)

    merged_expr = " ".join(merged_parts)

    try:
        human = humanize(merged_expr)
    except Exception:
        human = merged_expr

    return MergeResult(
        expression_a=expr_a,
        expression_b=expr_b,
        merged=merged_expr,
        human_readable=human,
        fields_unified=unified_fields,
    )
