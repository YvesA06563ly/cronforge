"""Group multiple cron expressions by shared field patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from cronforge.parser import CronExpression, CronParseError


class GrouperError(Exception):
    """Raised when grouping fails."""


@dataclass
class GroupResult:
    """Result of grouping cron expressions by a shared field."""

    group_by: str
    groups: Dict[str, List[str]]
    ungrouped: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Grouped by field: {self.group_by}"]
        for key, exprs in self.groups.items():
            lines.append(f"  [{key}]: {len(exprs)} expression(s)")
            for expr in exprs:
                lines.append(f"    - {expr}")
        if self.ungrouped:
            lines.append(f"  [unparseable]: {len(self.ungrouped)} expression(s)")
            for expr in self.ungrouped:
                lines.append(f"    - {expr}")
        return "\n".join(lines)


_FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]
_FIELD_INDEX = {name: i for i, name in enumerate(_FIELD_NAMES)}


def group(expressions: List[str], group_by: str = "hour") -> GroupResult:
    """Group *expressions* by the raw token of *group_by* field.

    Args:
        expressions: List of cron expression strings.
        group_by: One of ``minute``, ``hour``, ``dom``, ``month``, ``dow``.

    Returns:
        :class:`GroupResult` mapping field tokens to matching expressions.

    Raises:
        GrouperError: If *group_by* is not a valid field name.
    """
    if group_by not in _FIELD_INDEX:
        raise GrouperError(
            f"Invalid group_by field '{group_by}'. "
            f"Choose from: {', '.join(_FIELD_NAMES)}"
        )

    idx = _FIELD_INDEX[group_by]
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for raw in expressions:
        try:
            parsed = CronExpression(raw)
        except CronParseError:
            ungrouped.append(raw)
            continue

        fields = [parsed.minute, parsed.hour, parsed.dom, parsed.month, parsed.dow]
        key = fields[idx].raw
        groups.setdefault(key, []).append(raw)

    return GroupResult(group_by=group_by, groups=groups, ungrouped=ungrouped)
