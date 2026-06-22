"""TYPE_B (Monthly Card) transformation strategy — with overtime breakdown."""

from __future__ import annotations

import dataclasses
import logging

from ...domain.models import AttendanceRow
from ...domain.rules import get_rules
from ...domain.time_utils import hours_between, shift_time
from .base import TransformationStrategy
from .factory import StrategyFactory
from .seed import row_rng

logger = logging.getLogger(__name__)


@StrategyFactory.register
class TypeBTransformationStrategy(TransformationStrategy):
    """Per-row jitter, recomputed hours, plus a 125% overtime figure."""

    report_type = "TYPE_B"

    def transform_row(self, row: AttendanceRow, base_seed: int) -> AttendanceRow:
        rules = get_rules(self.report_type)
        rng = row_rng(base_seed, row)

        entry = shift_time(row.entry_time, rng.randint(0, rules.entry_jitter_mod))
        exit_time = shift_time(row.exit_time, -rng.randint(0, rules.exit_jitter_mod))

        worked = hours_between(entry, exit_time)
        total = row.total_hours if worked is None else round(max(0.0, worked), 2)

        overtime = max(0.0, total - rules.standard_daily_hours)
        overtime_125 = round(min(overtime, rules.overtime_125_cap_hours), 2)

        result = dataclasses.replace(
            row,
            entry_time=entry,
            exit_time=exit_time,
            total_hours=total,
            overtime_125_hours=overtime_125,
        )
        logger.debug(
            "TYPE_B [%s]: %s->%s, %s->%s, total=%s, 125%%=%s",
            row.date, row.entry_time, entry, row.exit_time, exit_time,
            total, overtime_125,
        )
        return result
