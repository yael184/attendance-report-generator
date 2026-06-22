"""Unit tests for the TransformationService (subject) and observers."""

from __future__ import annotations

import dataclasses

from attendance_report.application.observers import StatisticsObserver
from attendance_report.application.service import TransformationService
from attendance_report.application.transformation.base import TransformationStrategy
from attendance_report.application.transformation.validating_decorator import (
    ValidatingStrategyDecorator,
)
from attendance_report.domain.models import AttendanceRow


class _PassThrough(TransformationStrategy):
    def transform_row(self, row: AttendanceRow, base_seed: int) -> AttendanceRow:
        return row


def _service(strategy: TransformationStrategy, observer: StatisticsObserver):
    return TransformationService(
        strategy_registry={"TYPE_A": strategy}, observers=[observer]
    )


def test_service_notifies_observer_on_success(sample_row) -> None:
    stats = StatisticsObserver()
    service = _service(_PassThrough(), stats)
    result = service.transform("TYPE_A", [sample_row], base_seed=1)
    assert len(result) == 1
    assert stats.transformed == 1
    assert stats.failed == 0


def test_service_keeps_original_on_validation_failure(sample_row) -> None:
    bad = dataclasses.replace(sample_row, entry_time="17:00", exit_time="08:00")
    stats = StatisticsObserver()
    service = _service(ValidatingStrategyDecorator(_PassThrough(), "TYPE_A"), stats)
    result = service.transform("TYPE_A", [bad], base_seed=1)
    assert result == [bad]  # original preserved
    assert stats.failed == 1


def test_service_unknown_type_returns_unchanged(sample_row) -> None:
    service = TransformationService(strategy_registry={})
    result = service.transform("TYPE_X", [sample_row], base_seed=1)
    assert result == [sample_row]


def test_add_observer_at_runtime(sample_row) -> None:
    service = TransformationService(strategy_registry={"TYPE_A": _PassThrough()})
    stats = StatisticsObserver()
    service.add_observer(stats)
    service.transform("TYPE_A", [sample_row], base_seed=1)
    assert stats.transformed == 1
