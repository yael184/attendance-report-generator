"""TransformationService — the Observer *subject*.

Applies the right (decorated) strategy to every row of a report and notifies
its observers about what happens.  When the validating decorator rejects a
transformed row, the service keeps the original row and emits a
``validation_failed`` event rather than aborting the whole report.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Sequence

from ..domain.exceptions import ValidationError
from ..domain.models import AttendanceRow
from .observers import TransformationObserver
from .transformation.base import TransformationStrategy

logger = logging.getLogger(__name__)


class TransformationService:
    """Drives row transformations through a strategy registry + observers."""

    def __init__(
        self,
        strategy_registry: Dict[str, TransformationStrategy],
        observers: Sequence[TransformationObserver] | None = None,
    ) -> None:
        self._registry = strategy_registry
        self._observers: List[TransformationObserver] = list(observers or [])

    def add_observer(self, observer: TransformationObserver) -> None:
        """Subscribe an observer at runtime."""
        self._observers.append(observer)

    def transform(
        self, report_type: str, rows: Sequence[AttendanceRow], base_seed: int
    ) -> List[AttendanceRow]:
        strategy = self._registry.get(report_type)
        if strategy is None:
            logger.warning(
                "No strategy for '%s' — returning rows unchanged", report_type
            )
            return list(rows)

        self._notify("on_started", report_type, len(rows))

        result: List[AttendanceRow] = []
        for row in rows:
            if not row.entry_time or not row.exit_time:
                result.append(row)
                continue
            try:
                transformed = strategy.transform_row(row, base_seed)
                result.append(transformed)
                self._notify("on_row_transformed", row, transformed)
            except ValidationError as exc:
                result.append(row)  # rows are frozen — safe to reuse
                self._notify("on_validation_failed", row, exc)

        self._notify("on_completed", report_type, len(result))
        return result

    def _notify(self, event: str, *args: object) -> None:
        for observer in self._observers:
            getattr(observer, event)(*args)
