"""Observer pattern for transformation events.

The :class:`~attendance_report.application.service.TransformationService`
(the *subject*) emits lifecycle events without knowing who — if anyone — is
listening.  Observers subscribe by being passed in the service's constructor,
so adding a new listener (metrics, auditing, progress bar …) needs **no**
change to the service.

The base class provides no-op defaults so a concrete observer only overrides
the events it cares about.
"""

from __future__ import annotations

import logging

from ..domain.models import AttendanceRow

logger = logging.getLogger(__name__)


class TransformationObserver:
    """Base observer. Override only the hooks you need."""

    def on_started(self, report_type: str, total_rows: int) -> None: ...

    def on_row_transformed(
        self, original: AttendanceRow, transformed: AttendanceRow
    ) -> None: ...

    def on_validation_failed(self, row: AttendanceRow, error: Exception) -> None: ...

    def on_completed(self, report_type: str, transformed_rows: int) -> None: ...


class LoggingObserver(TransformationObserver):
    """Writes transformation progress to the logging system."""

    def on_started(self, report_type: str, total_rows: int) -> None:
        logger.info("Transforming %d row(s) as %s", total_rows, report_type)

    def on_row_transformed(
        self, original: AttendanceRow, transformed: AttendanceRow
    ) -> None:
        logger.debug(
            "Row %s: %s-%s -> %s-%s",
            original.date,
            original.entry_time,
            original.exit_time,
            transformed.entry_time,
            transformed.exit_time,
        )

    def on_validation_failed(self, row: AttendanceRow, error: Exception) -> None:
        logger.warning("Validation failed on %s: %s — keeping original", row.date, error)

    def on_completed(self, report_type: str, transformed_rows: int) -> None:
        logger.info("Transformation complete: %d row(s)", transformed_rows)


class StatisticsObserver(TransformationObserver):
    """Collects simple counters; handy for tests and summaries."""

    def __init__(self) -> None:
        self.transformed = 0
        self.failed = 0

    def on_row_transformed(
        self, original: AttendanceRow, transformed: AttendanceRow
    ) -> None:
        self.transformed += 1

    def on_validation_failed(self, row: AttendanceRow, error: Exception) -> None:
        self.failed += 1
