"""Unit tests for the validating decorator."""

from __future__ import annotations

import dataclasses

import pytest

from attendance_report.application.transformation.base import TransformationStrategy
from attendance_report.application.transformation.validating_decorator import (
    ValidatingStrategyDecorator,
)
from attendance_report.domain.exceptions import ValidationError
from attendance_report.domain.models import AttendanceRow


class _PassThrough(TransformationStrategy):
    """Test strategy: returns the row unchanged."""

    def transform_row(self, row: AttendanceRow, base_seed: int) -> AttendanceRow:
        return row


def test_decorator_accepts_valid_row(sample_row) -> None:
    decorated = ValidatingStrategyDecorator(_PassThrough(), "TYPE_A")
    assert decorated.transform_row(sample_row, 0) == sample_row


def test_decorator_rejects_exit_before_entry(sample_row) -> None:
    bad = dataclasses.replace(sample_row, entry_time="17:00", exit_time="08:00")
    decorated = ValidatingStrategyDecorator(_PassThrough(), "TYPE_A")
    with pytest.raises(ValidationError):
        decorated.transform_row(bad, 0)


def test_decorator_rejects_entry_out_of_range(sample_row) -> None:
    bad = dataclasses.replace(sample_row, entry_time="04:00", exit_time="17:00")
    decorated = ValidatingStrategyDecorator(_PassThrough(), "TYPE_A")
    with pytest.raises(ValidationError):
        decorated.transform_row(bad, 0)


def test_decorator_can_wrap_another_decorator(sample_row) -> None:
    # Stacking decorators works because each implements the same interface.
    inner = ValidatingStrategyDecorator(_PassThrough(), "TYPE_A")
    outer = ValidatingStrategyDecorator(inner, "TYPE_A")
    assert outer.transform_row(sample_row, 0) == sample_row
