"""Unit tests for the pure time helpers."""

from __future__ import annotations

import pytest

from attendance_report.domain.time_utils import (
    break_to_minutes,
    hours_between,
    is_valid_hours_value,
    is_valid_time_format,
    normalize_time,
    shift_time,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("6.30", "06:30"),
        ("18.30", "18:30"),
        ("6:30", "06:30"),
        ("18:30", "18:30"),
        ("630", "06:30"),
        ("1830", "18:30"),
        ("8:04", "08:04"),
        ("8.04", "08:04"),
    ],
)
def test_normalize_time(raw: str, expected: str) -> None:
    assert normalize_time(raw) == expected


def test_normalize_time_invalid_returns_original() -> None:
    assert normalize_time("99:99") == "99:99"
    assert normalize_time("") == ""


@pytest.mark.parametrize(
    "value, expected",
    [
        ("8:04", True),
        ("08:00", True),
        ("630", True),
        ("1830", True),
        ("25:00", False),
        ("18:70", False),
        ("6.5", False),  # decimal hours, not a clock time
    ],
)
def test_is_valid_time_format(value: str, expected: bool) -> None:
    assert is_valid_time_format(value) is expected


@pytest.mark.parametrize(
    "value, expected",
    [("6.50", True), ("350", True), ("1440", True), ("0", True), ("1500", False)],
)
def test_is_valid_hours_value(value: str, expected: bool) -> None:
    assert is_valid_hours_value(value) is expected


def test_shift_time() -> None:
    assert shift_time("08:00", 15) == "08:15"
    assert shift_time("08:00", -10) == "07:50"
    assert shift_time("bad", 10) == "bad"


def test_hours_between() -> None:
    assert hours_between("08:00", "17:00") == 9.0
    assert hours_between("08:00", "12:30") == 4.5
    assert hours_between("bad", "17:00") is None


def test_break_to_minutes() -> None:
    assert break_to_minutes("01:30") == 90
    assert break_to_minutes("00:00") == 0
    assert break_to_minutes(None) == 0
    assert break_to_minutes("garbage") == 0
