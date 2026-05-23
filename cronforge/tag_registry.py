"""In-memory registry for storing and querying tagged cron expressions."""

from __future__ import annotations

from typing import Dict, Iterator, List

from cronforge.tagger import TagResult, tag, TaggerError


class RegistryError(Exception):
    """Raised on registry operation failures."""


class TagRegistry:
    """Stores :class:`~cronforge.tagger.TagResult` objects keyed by expression."""

    def __init__(self) -> None:
        self._store: Dict[str, TagResult] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def register(self, expression: str) -> TagResult:
        """Tag *expression* and add it to the registry; return the result."""
        try:
            result = tag(expression)
        except TaggerError as exc:
            raise RegistryError(str(exc)) from exc
        self._store[expression] = result
        return result

    def remove(self, expression: str) -> None:
        """Remove *expression* from the registry (no-op if absent)."""
        self._store.pop(expression, None)

    def clear(self) -> None:
        """Remove all entries."""
        self._store.clear()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._store)

    def __iter__(self) -> Iterator[TagResult]:
        return iter(self._store.values())

    def __contains__(self, expression: object) -> bool:
        return expression in self._store

    def find_by_tag(self, label: str) -> List[TagResult]:
        """Return all results that carry *label*."""
        return [r for r in self._store.values() if label in r.tags]

    def all_tags(self) -> List[str]:
        """Return a sorted, deduplicated list of every tag present in the registry."""
        seen: set[str] = set()
        for result in self._store.values():
            seen.update(result.tags)
        return sorted(seen)
