"""TYPE_A (Eagle) transformation strategy — break-aware hour calculation."""

from __future__ import annotations

import dataclasses
import logging

from ...domain.models import AttendanceRow
from ...domain.rules import get_rules
from ...domain.time_utils import break_to_minutes, hours_between, shift_time
from .base import TransformationStrategy
from .factory import StrategyFactory
from .seed import row_rng

logger = logging.getLogger(__name__)


@StrategyFactory.register
class TypeATransformationStrategy(TransformationStrategy):
    """Applies a deterministic per-row jitter and recomputes total hours."""

    report_type = "TYPE_A"

    def transform_row(self, row: AttendanceRow, base_seed: int) -> AttendanceRow:
        rules = get_rules(self.report_type)
        rng = row_rng(base_seed, row)

        entry = shift_time(row.entry_time, rng.randint(0, rules.entry_jitter_mod))
        exit_time = shift_time(row.exit_time, -rng.randint(0, rules.exit_jitter_mod))

        worked = hours_between(entry, exit_time)
        if worked is None:
            total = row.total_hours
        else:
            total = round(max(0.0, worked - break_to_minutes(row.break_duration) / 60), 2)

        result = dataclasses.replace(
            row, entry_time=entry, exit_time=exit_time, total_hours=total
        )
        logger.debug(
            "TYPE_A [%s]: %s->%s, %s->%s, total=%s",
            row.date, row.entry_time, entry, row.exit_time, exit_time, total,
        )
        return result
