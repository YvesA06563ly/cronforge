"""Cron expression parser and validator for cronforge."""

import re
from dataclasses import dataclass
from typing import Optional

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}

FIELD_NAMES = list(FIELD_RANGES.keys())

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronField:
    name: str
    raw: str
    values: list[int]


@dataclass
class CronExpression:
    raw: str
    fields: dict[str, CronField]

    def __str__(self) -> str:
        return self.raw


class CronParseError(ValueError):
    pass


def _resolve_alias(value: str, aliases: dict[str, int]) -> str:
    return str(aliases[value.lower()]) if value.lower() in aliases else value


def _parse_field(raw: str, field_name: str) -> CronField:
    min_val, max_val = FIELD_RANGES[field_name]
    aliases = MONTH_ALIASES if field_name == "month" else DOW_ALIASES if field_name == "day_of_week" else {}
    values: set[int] = set()

    for part in raw.split(","):
        part = _resolve_alias(part, aliases)
        if part == "*":
            values.update(range(min_val, max_val + 1))
        elif re.match(r"^\*/\d+$", part):
            step = int(part.split("/")[1])
            if step == 0:
                raise CronParseError(f"Step cannot be zero in field '{field_name}'")
            values.update(range(min_val, max_val + 1, step))
        elif re.match(r"^\d+-\d+$", part):
            start, end = map(int, part.split("-"))
            if start > end:
                raise CronParseError(f"Invalid range '{part}' in field '{field_name}'")
            values.update(range(start, end + 1))
        elif re.match(r"^\d+-\d+/\d+$", part):
            range_part, step = part.split("/")
            start, end = map(int, range_part.split("-"))
            values.update(range(start, end + 1, int(step)))
        elif re.match(r"^\d+$", part):
            values.add(int(part))
        else:
            raise CronParseError(f"Invalid token '{part}' in field '{field_name}'")

    out_of_range = [v for v in values if not (min_val <= v <= max_val)]
    if out_of_range:
        raise CronParseError(
            f"Values {out_of_range} out of range [{min_val}-{max_val}] for field '{field_name}'"
        )

    return CronField(name=field_name, raw=raw, values=sorted(values))


def parse(expression: str) -> CronExpression:
    """Parse a standard 5-field cron expression and return a CronExpression."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise CronParseError(
            f"Expected 5 fields, got {len(parts)}: '{expression}'"
        )
    fields = {
        name: _parse_field(raw, name)
        for name, raw in zip(FIELD_NAMES, parts)
    }
    return CronExpression(raw=expression, fields=fields)
