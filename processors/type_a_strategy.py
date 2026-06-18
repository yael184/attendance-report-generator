import copy
from datetime import datetime, timedelta

from core.models import AttendanceRow
from processors.transformation_strategy import BaseTransformationStrategy
from utils.time_handler import normalize_time
from logger_config import get_logger

logger = get_logger(__name__)


class TypeATransformationStrategy(BaseTransformationStrategy):
    """Transformation strategy for Eagle (TYPE_A) reports with break-aware hour calculation."""

    def transform_row(self, row: AttendanceRow, seed: int) -> AttendanceRow:
        result = copy.copy(row)

        jitter_entry = seed % 7
        jitter_exit = -(seed % 4)

        result.entry_time = self._adjust_time(row.entry_time, jitter_entry)
        result.exit_time = self._adjust_time(row.exit_time, jitter_exit)
        result.total_hours = self._compute_hours(
            result.entry_time, result.exit_time, row.break_duration, row.total_hours
        )

        logger.debug(
            f"TYPE_A transform [{row.date}]: "
            f"{row.entry_time}->{result.entry_time}, "
            f"{row.exit_time}->{result.exit_time}, "
            f"total={result.total_hours}"
        )
        return result

    def _adjust_time(self, time_str: str, offset_minutes: int) -> str:
        if not time_str:
            return time_str
        normalized = normalize_time(time_str)
        if not normalized or ":" not in normalized:
            return time_str
        try:
            t = datetime.strptime(normalized, "%H:%M")
            return (t + timedelta(minutes=offset_minutes)).strftime("%H:%M")
        except ValueError:
            return time_str

    def _compute_hours(
        self, entry: str, exit_t: str, break_duration: str, fallback: float
    ) -> float:
        try:
            e = datetime.strptime(entry, "%H:%M")
            x = datetime.strptime(exit_t, "%H:%M")
            total = (x - e).total_seconds() / 3600
            if break_duration and break_duration not in ("00:00", ""):
                parts = break_duration.split(":")
                total -= int(parts[0]) + int(parts[1]) / 60
            return round(max(0.0, total), 2)
        except (ValueError, AttributeError, IndexError):
            return fallback
