"""Unit tests for the frozen domain models."""

from __future__ import annotations

import dataclasses

import pytest

from attendance_report.domain.models import AttendanceReport, AttendanceRow


def test_row_is_frozen(sample_row: AttendanceRow) -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        sample_row.entry_time = "09:00"  # type: ignore[misc]


def test_replace_creates_new_row(sample_row: AttendanceRow) -> None:
    updated = dataclasses.replace(sample_row, entry_time="09:00")
    assert updated.entry_time == "09:00"
    assert sample_row.entry_time == "08:00"  # original untouched
    assert updated is not sample_row


def test_report_from_rows_aggregates() -> None:
    rows = (
        AttendanceRow("01/05", "", "08:00", "17:00", 9.0),
        AttendanceRow("02/05", "", "08:00", "16:00", 8.0),
    )
    report = AttendanceReport.from_rows("TYPE_A", rows)
    assert report.total_days == 2
    assert report.total_monthly_hours == 17.0
    assert report.rows == rows
