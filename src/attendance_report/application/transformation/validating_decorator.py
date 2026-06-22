"""Validating Decorator.

Wraps *any* :class:`TransformationStrategy` (a concrete strategy or even
another decorator) and validates the produced row against the variant's
business rules.  Because it implements the same interface as the thing it
wraps, callers cannot tell the difference — and decorators can be stacked.

It does not know whether the inner object is TypeA, TypeB or another
decorator; it only knows the ``TransformationStrategy`` contract.
"""

from __future__ import annotations

import logging

from ...domain.exceptions import ValidationError
from ...domain.models import AttendanceRow
from ...domain.rules import VariantRules, get_rules
from ...domain.time_utils import break_to_minutes
from .base import TransformationStrategy

logger = logging.getLogger(__name__)


class ValidatingStrategyDecorator(TransformationStrategy):
    """Decorator enforcing per-variant rules on the wrapped strategy's output."""

    def __init__(
        self, inner: TransformationStrategy, report_type: str
    ) -> None:
        self._inner = inner
        self._rules: VariantRules = get_rules(report_type)
        self._report_type = report_type

    def transform_row(self, row: AttendanceRow, base_seed: int) -> AttendanceRow:
        result = self._inner.transform_row(row, base_seed)
        self._validate(result)
        return result

    def _validate(self, row: AttendanceRow) -> None:
        if not row.entry_time or not row.exit_time:
            return

        rules = self._rules
        if row.exit_time <= row.entry_time:
            raise ValidationError(
                f"exit {row.exit_time} not after entry {row.entry_time} on {row.date}"
            )
        if not (rules.entry_min <= row.entry_time <= rules.entry_max):
            raise ValidationError(
                f"entry {row.entry_time} outside "
                f"[{rules.entry_min}, {rules.entry_max}] on {row.date}"
            )
        if not (rules.exit_min <= row.exit_time <= rules.exit_max):
            raise ValidationError(
                f"exit {row.exit_time} outside "
                f"[{rules.exit_min}, {rules.exit_max}] on {row.date}"
            )
        if break_to_minutes(row.break_duration) > rules.break_max_minutes:
            raise ValidationError(
                f"break {row.break_duration} exceeds "
                f"{rules.break_max_minutes} minutes on {row.date}"
            )
