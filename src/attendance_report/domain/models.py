"""Immutable domain models — the *unified* representation both report types
are normalised into.

Every model is ``frozen=True`` so a row can never be mutated in place: a
transformation produces a **new** row via :func:`dataclasses.replace`.  This
removes a whole class of "spooky action at a distance" bugs and makes the
pipeline trivially testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional, Tuple

_EMPTY_METADATA: Mapping[str, str] = MappingProxyType({})


@dataclass(frozen=True, slots=True)
class AttendanceRow:
    """A single day of attendance, unified across all report variants.

    TYPE_A (Eagle) and TYPE_B (Monthly Card) both normalise into this shape;
    the optional fields simply stay ``None`` for variants that do not use
    them.  Adding a third report variant requires *no* change here.
    """

    date: str
    day_of_week: str
    entry_time: str
    exit_time: str
    total_hours: float
    location: Optional[str] = None
    break_duration: str = "00:00"
    # TYPE_B (Monthly Card) optional overtime breakdown
    break_minutes: Optional[int] = None
    overtime_125_hours: Optional[float] = None
    overtime_150_hours: Optional[float] = None
    overtime_shabbat_hours: Optional[float] = None
    raw_metadata: Mapping[str, str] = field(default_factory=lambda: _EMPTY_METADATA)


@dataclass(frozen=True, slots=True)
class AttendanceReport:
    """A whole parsed report: header info plus an immutable tuple of rows."""

    report_type: str
    employee_name: Optional[str]
    month_year: str
    rows: Tuple[AttendanceRow, ...]
    total_monthly_hours: float
    total_days: int

    @classmethod
    def from_rows(
        cls,
        report_type: str,
        rows: Tuple[AttendanceRow, ...],
        employee_name: Optional[str] = None,
        month_year: str = "",
    ) -> "AttendanceReport":
        """Build a report from rows, deriving the aggregate totals."""
        total_hours = round(sum(row.total_hours for row in rows), 2)
        return cls(
            report_type=report_type,
            employee_name=employee_name,
            month_year=month_year,
            rows=tuple(rows),
            total_monthly_hours=total_hours,
            total_days=len(rows),
        )
