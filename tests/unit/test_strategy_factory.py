"""Unit tests for the transformation StrategyFactory/registry."""

from __future__ import annotations

import pytest

from attendance_report.application.transformation.factory import StrategyFactory
from attendance_report.application.transformation.validating_decorator import (
    ValidatingStrategyDecorator,
)
from attendance_report.domain.exceptions import ConfigurationError


def test_registry_has_both_types() -> None:
    assert set(StrategyFactory.available_types()) >= {"TYPE_A", "TYPE_B"}


def test_create_validated_wraps_in_decorator() -> None:
    strategy = StrategyFactory.create_validated("TYPE_A")
    assert isinstance(strategy, ValidatingStrategyDecorator)


def test_build_registry_covers_all_types() -> None:
    registry = StrategyFactory.build_registry(validated=True)
    assert set(registry) == set(StrategyFactory.available_types())


def test_unknown_strategy_raises() -> None:
    with pytest.raises(ConfigurationError):
        StrategyFactory.create("TYPE_NOPE")
