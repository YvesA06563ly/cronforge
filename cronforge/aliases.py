"""Named alias registry for common cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class AliasError(Exception):
    """Raised when an alias operation fails."""


# Built-in well-known aliases
_BUILTIN_ALIASES: Dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@every_minute": "* * * * *",
    "@every_5_minutes": "*/5 * * * *",
    "@every_15_minutes": "*/15 * * * *",
    "@every_30_minutes": "*/30 * * * *",
    "@workdays": "0 9 * * 1-5",
    "@weekends": "0 10 * * 6,0",
}


@dataclass
class AliasResult:
    name: str
    expression: str
    source: str  # "builtin" or "user"
    description: Optional[str] = None

    def summary(self) -> str:
        desc = f" — {self.description}" if self.description else ""
        return f"{self.name} ({self.source}): {self.expression}{desc}"


@dataclass
class AliasRegistry:
    _user: Dict[str, AliasResult] = field(default_factory=dict)

    def register(self, name: str, expression: str, description: Optional[str] = None) -> AliasResult:
        """Register a user-defined alias."""
        if not name.startswith("@"):
            raise AliasError(f"Alias name must start with '@', got: {name!r}")
        if name in _BUILTIN_ALIASES:
            raise AliasError(f"Cannot override built-in alias: {name!r}")
        result = AliasResult(name=name, expression=expression, source="user", description=description)
        self._user[name] = result
        return result

    def remove(self, name: str) -> None:
        """Remove a user-defined alias."""
        if name not in self._user:
            raise AliasError(f"User alias not found: {name!r}")
        del self._user[name]

    def resolve(self, name: str) -> AliasResult:
        """Resolve an alias name to its expression."""
        if name in self._user:
            return self._user[name]
        if name in _BUILTIN_ALIASES:
            return AliasResult(name=name, expression=_BUILTIN_ALIASES[name], source="builtin")
        raise AliasError(f"Unknown alias: {name!r}")

    def list_all(self) -> List[AliasResult]:
        """Return all known aliases (builtins + user-defined)."""
        results: List[AliasResult] = [
            AliasResult(name=k, expression=v, source="builtin")
            for k, v in _BUILTIN_ALIASES.items()
        ]
        results.extend(self._user.values())
        return results

    def lookup_expression(self, expression: str) -> List[AliasResult]:
        """Find all aliases that map to a given expression."""
        return [r for r in self.list_all() if r.expression == expression]


# Module-level default registry
default_registry = AliasRegistry()
