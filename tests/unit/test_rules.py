"""Unit tests for the rules registry."""

from __future__ import annotations

import dataclasses

import pytest

from attendance_report.domain.exceptions import ConfigurationError
from attendance_report.domain.rules import RULES_REGISTRY, get_rules


def test_known_variants_present() -> None:
    assert "TYPE_A" in RULES_REGISTRY
    assert "TYPE_B" in RULES_REGISTRY


def test_get_rules_returns_registered() -> None:
    rules = get_rules("TYPE_A")
    assert rules is RULES_REGISTRY["TYPE_A"]


def test_rules_are_frozen() -> None:
    rules = get_rules("TYPE_A")
    with pytest.raises(dataclasses.FrozenInstanceError):
        rules.break_max_minutes = 999  # type: ignore[misc]


def test_unknown_variant_falls_back() -> None:
    assert get_rules("TYPE_Z") is RULES_REGISTRY["TYPE_A"]


def test_unknown_variant_strict_raises() -> None:
    with pytest.raises(ConfigurationError):
        get_rules("TYPE_Z", strict=True)
