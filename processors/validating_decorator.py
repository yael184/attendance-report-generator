from core.models import AttendanceRow
from processors.transformation_strategy import BaseTransformationStrategy
from logger_config import get_logger

logger = get_logger(__name__)


class TransformationError(Exception):
    pass


class ValidatingStrategyDecorator(BaseTransformationStrategy):
    """
    Decorator that wraps a transformation strategy and validates its output.
    Raises TransformationError if the result violates business rules so that
    TransformationService can fall back to the original row.
    """

    ENTRY_MIN = "05:00"
    ENTRY_MAX = "11:00"
    EXIT_MIN = "13:00"
    EXIT_MAX = "23:59"
    BREAK_MAX_MINUTES = 90

    def __init__(self, inner: BaseTransformationStrategy):
        self._inner = inner

    def transform_row(self, row: AttendanceRow, seed: int) -> AttendanceRow:
        result = self._inner.transform_row(row, seed)
        self._validate(result)
        return result

    def _validate(self, row: AttendanceRow) -> None:
        if not row.entry_time or not row.exit_time:
            return

        if row.exit_time <= row.entry_time:
            raise TransformationError(
                f"exit {row.exit_time} not after entry {row.entry_time} on {row.date}"
            )

        if not (self.ENTRY_MIN <= row.entry_time <= self.ENTRY_MAX):
            raise TransformationError(
                f"entry {row.entry_time} outside [{self.ENTRY_MIN}, {self.ENTRY_MAX}]"
            )

        if not (self.EXIT_MIN <= row.exit_time <= self.EXIT_MAX):
            raise TransformationError(
                f"exit {row.exit_time} outside [{self.EXIT_MIN}, {self.EXIT_MAX}]"
            )

        if row.break_duration and row.break_duration not in ("00:00", ""):
            try:
                parts = row.break_duration.split(":")
                break_minutes = int(parts[0]) * 60 + int(parts[1])
                if break_minutes > self.BREAK_MAX_MINUTES:
                    raise TransformationError(
                        f"break {row.break_duration} exceeds {self.BREAK_MAX_MINUTES} minutes"
                    )
            except (ValueError, IndexError):
                pass
