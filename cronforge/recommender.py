"""Recommender: suggest simpler or equivalent cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cronforge.parser import CronExpression, CronParseError


class RecommenderError(Exception):
    """Raised when the recommender encounters an unrecoverable problem."""


@dataclass
class RecommendResult:
    expression: str
    suggestions: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if not self.suggestions:
            return f"{self.expression}: no simpler equivalent found."
        lines = [f"{self.expression}: {len(self.suggestions)} suggestion(s)"]
        for s in self.suggestions:
            lines.append(f"  -> {s}")
        for n in self.notes:
            lines.append(f"  note: {n}")
        return "\n".join(lines)


def _is_wildcard(value: str) -> bool:
    return value == "*"


def _is_step_one(value: str) -> bool:
    """Detect patterns like */1 or 0-59/1."""
    if "/" in value:
        _, step = value.rsplit("/", 1)
        return step == "1"
    return False


def _simplify_field(raw: str) -> str | None:
    """Return a simpler representation or None if already minimal."""
    if _is_step_one(raw):
        base = raw.split("/")[0]
        return "*" if base in ("*", "0-59", "0-23", "0-31", "1-12", "0-7") else None
    return None


def recommend(expression: str) -> RecommendResult:
    """Analyse *expression* and return simplification suggestions."""
    try:
        parsed = CronExpression.parse(expression)
    except CronParseError as exc:
        raise RecommenderError(f"Cannot parse expression: {exc}") from exc

    fields_raw = expression.split()
    if len(fields_raw) != 5:
        raise RecommenderError("Expression must have exactly 5 fields.")

    labels = ["minute", "hour", "day-of-month", "month", "day-of-week"]
    simplified = list(fields_raw)
    notes: List[str] = []
    changed = False

    for i, raw in enumerate(fields_raw):
        better = _simplify_field(raw)
        if better is not None:
            notes.append(f"{labels[i]} '{raw}' can be written as '{better}'")
            simplified[i] = better
            changed = True

    # Suggest @reboot / @daily / @hourly aliases where applicable
    suggestions: List[str] = []
    if changed:
        suggestions.append(" ".join(simplified))

    canonical_aliases = {
        "0 0 * * *": "@daily",
        "0 * * * *": "@hourly",
        "* * * * *": "@every_minute",
        "0 0 * * 0": "@weekly",
        "0 0 1 * *": "@monthly",
        "0 0 1 1 *": "@yearly",
    }
    candidate = " ".join(simplified)
    if candidate in canonical_aliases:
        alias = canonical_aliases[candidate]
        suggestions.append(alias)
        notes.append(f"equivalent to the well-known alias {alias}")
    elif expression in canonical_aliases:
        alias = canonical_aliases[expression]
        suggestions.append(alias)
        notes.append(f"equivalent to the well-known alias {alias}")

    return RecommendResult(expression=expression, suggestions=suggestions, notes=notes)
