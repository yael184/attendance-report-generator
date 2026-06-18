import copy
from typing import Dict, List

from core.models import AttendanceRow
from processors.transformation_strategy import BaseTransformationStrategy
from processors.validating_decorator import TransformationError
from logger_config import get_logger

logger = get_logger(__name__)


class TransformationService:
    """
    Applies deterministic transformations to attendance rows using a strategy registry.
    Falls back to the original row when the decorated strategy raises TransformationError.
    """

    def __init__(self, strategy_registry: Dict[str, BaseTransformationStrategy]):
        self._registry = strategy_registry

    def transform(
        self, report_type: str, rows: List[AttendanceRow], seed: int
    ) -> List[AttendanceRow]:
        strategy = self._registry.get(report_type)
        if not strategy:
            logger.warning(f"No transformation strategy for type '{report_type}' — returning original rows")
            return rows

        result: List[AttendanceRow] = []
        for row in rows:
            if not row.entry_time or not row.exit_time:
                result.append(row)
                continue
            try:
                result.append(strategy.transform_row(row, seed))
            except TransformationError as exc:
                logger.warning(f"Validation failed on {row.date}: {exc} — keeping original row")
                result.append(copy.copy(row))

        return result
