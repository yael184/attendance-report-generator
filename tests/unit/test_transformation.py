"""Unit tests for the transformation strategies."""

from __future__ import annotations

import dataclasses

from attendance_report.application.transformation.type_a import (
    TypeATransformationStrategy,
)
from attendance_report.application.transformation.type_b import (
    TypeBTransformationStrategy,
)


def test_type_a_is_deterministic(sample_row) -> None:
    strategy = TypeATransformationStrategy()
    first = strategy.transform_row(sample_row, base_seed=123)
    second = strategy.transform_row(sample_row, base_seed=123)
    assert first == second


def test_type_a_does_not_mutate_input(sample_row) -> None:
    TypeATransformationStrategy().transform_row(sample_row, base_seed=5)
    assert sample_row.entry_time == "08:00"
    assert sample_row.exit_time == "17:00"


def test_type_a_recomputes_hours(sample_row) -> None:
    result = TypeATransformationStrategy().transform_row(sample_row, base_seed=5)
    # entry shifts forward, exit shifts back -> worked time <= 9h
    assert 0 < result.total_hours <= 9.0


def test_different_dates_vary_independently(sample_row) -> None:
    strategy = TypeATransformationStrategy()
    other = dataclasses.replace(sample_row, date="15/06/2024")
    r1 = strategy.transform_row(sample_row, base_seed=10)
    r2 = strategy.transform_row(other, base_seed=10)
    # Same base seed, different date -> independent (very likely different) jitter
    assert (r1.entry_time, r1.exit_time) != (r2.entry_time, r2.exit_time)


def test_type_b_adds_overtime(sample_row) -> None:
    long_day = dataclasses.replace(sample_row, entry_time="07:00", exit_time="19:00")
    result = TypeBTransformationStrategy().transform_row(long_day, base_seed=3)
    assert result.overtime_125_hours is not None
    assert result.overtime_125_hours > 0
