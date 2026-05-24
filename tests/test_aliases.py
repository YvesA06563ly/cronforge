"""Tests for cronforge.aliases module."""

import pytest

from cronforge.aliases import (
    AliasError,
    AliasRegistry,
    AliasResult,
    default_registry,
    _BUILTIN_ALIASES,
)


@pytest.fixture
def registry() -> AliasRegistry:
    return AliasRegistry()


def test_resolve_builtin_yearly(registry):
    result = registry.resolve("@yearly")
    assert result.expression == "0 0 1 1 *"
    assert result.source == "builtin"


def test_resolve_builtin_hourly(registry):
    result = registry.resolve("@hourly")
    assert result.expression == "0 * * * *"


def test_resolve_unknown_raises(registry):
    with pytest.raises(AliasError, match="Unknown alias"):
        registry.resolve("@nonexistent")


def test_register_user_alias(registry):
    result = registry.register("@deploy", "0 2 * * 1", description="Weekly deploy")
    assert isinstance(result, AliasResult)
    assert result.source == "user"
    assert result.expression == "0 2 * * 1"


def test_register_requires_at_prefix(registry):
    with pytest.raises(AliasError, match="must start with '@'"):
        registry.register("deploy", "0 2 * * 1")


def test_register_cannot_override_builtin(registry):
    with pytest.raises(AliasError, match="Cannot override built-in"):
        registry.register("@daily", "* * * * *")


def test_resolve_user_alias_after_register(registry):
    registry.register("@nightly", "0 3 * * *")
    result = registry.resolve("@nightly")
    assert result.expression == "0 3 * * *"
    assert result.source == "user"


def test_remove_user_alias(registry):
    registry.register("@cleanup", "0 4 * * 0")
    registry.remove("@cleanup")
    with pytest.raises(AliasError, match="Unknown alias"):
        registry.resolve("@cleanup")


def test_remove_nonexistent_raises(registry):
    with pytest.raises(AliasError, match="User alias not found"):
        registry.remove("@ghost")


def test_list_all_includes_builtins(registry):
    all_aliases = registry.list_all()
    names = [r.name for r in all_aliases]
    assert "@daily" in names
    assert "@hourly" in names
    assert "@weekly" in names


def test_list_all_includes_user_aliases(registry):
    registry.register("@myalias", "*/10 * * * *")
    names = [r.name for r in registry.list_all()]
    assert "@myalias" in names


def test_list_all_count(registry):
    all_aliases = registry.list_all()
    assert len(all_aliases) == len(_BUILTIN_ALIASES)


def test_lookup_expression_finds_both_yearly_aliases(registry):
    results = registry.lookup_expression("0 0 1 1 *")
    names = [r.name for r in results]
    assert "@yearly" in names
    assert "@annually" in names


def test_lookup_expression_no_match(registry):
    results = registry.lookup_expression("99 99 99 99 99")
    assert results == []


def test_summary_includes_name_and_expression(registry):
    result = registry.resolve("@daily")
    s = result.summary()
    assert "@daily" in s
    assert "0 0 * * *" in s


def test_summary_includes_description_when_present(registry):
    registry.register("@report", "0 6 * * 1", description="Monday reports")
    result = registry.resolve("@report")
    assert "Monday reports" in result.summary()


def test_default_registry_is_alias_registry():
    assert isinstance(default_registry, AliasRegistry)
