"""Pure time-handling helpers.

These functions are deliberately free of any I/O, logging or framework
dependency so they live in the domain layer and are trivial to unit-test.
They understand the messy formats that OCR produces (``6.30``, ``630``,
``18:30`` …) and normalise everything to ``HH:MM``.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional


def normalize_time(time_str: Optional[str]) -> str:
    """Convert any supported time format to canonical ``HH:MM``.

    Supported inputs include ``6.30``/``6:30``/``630`` (-> ``06:30``) and
    ``18.30``/``18:30``/``1830`` (-> ``18:30``).  If the value cannot be
    interpreted it is returned unchanged.
    """
    if not time_str:
        return time_str or ""

    value = time_str.strip().replace(".", ":")

    if ":" in value:
        parts = value.split(":")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            hours, minutes = parts[0].zfill(2), parts[1].zfill(2)
            if _is_valid_hm(hours, minutes):
                return f"{hours}:{minutes}"
        return time_str

    digits = "".join(c for c in value if c.isdigit())
    if len(digits) == 3:
        hours, minutes = digits[0].zfill(2), digits[1:3]
    elif len(digits) == 4:
        hours, minutes = digits[0:2], digits[2:4]
    else:
        return time_str

    if _is_valid_hm(hours, minutes):
        return f"{hours}:{minutes}"
    return time_str


def is_valid_time_format(value: Optional[str]) -> bool:
    """Return ``True`` if *value* looks like a clock time (entry/exit)."""
    if not value:
        return False

    check = value.replace(".", ":")
    if ":" in check:
        parts = check.split(":")
        if len(parts) == 2 and len(parts[1]) == 2:
            return _is_valid_hm(parts[0], parts[1])
        return False

    if "." in value:  # a decimal like 6.5 is hours, not a clock time
        return False

    digits = "".join(c for c in value if c.isdigit())
    if len(digits) == 3:
        return _is_valid_hm(digits[0], digits[1:3])
    if len(digits) == 4:
        return _is_valid_hm(digits[0:2], digits[2:4])
    return False


def is_valid_hours_value(value: Optional[str]) -> bool:
    """Return ``True`` if *value* looks like a total-hours figure."""
    if not value:
        return False
    try:
        val = float(value.replace(",", "."))
    except ValueError:
        return False
    return 0 <= val <= 1440


def shift_time(time_str: str, offset_minutes: int) -> str:
    """Return *time_str* shifted by *offset_minutes*, staying in ``HH:MM``.

    The value is normalised first; invalid input is returned unchanged.
    """
    normalized = normalize_time(time_str)
    if not normalized or ":" not in normalized:
        return time_str
    try:
        t = datetime.strptime(normalized, "%H:%M")
    except ValueError:
        return time_str
    return (t + timedelta(minutes=offset_minutes)).strftime("%H:%M")


def hours_between(entry: str, exit_time: str) -> Optional[float]:
    """Return the number of hours between two ``HH:MM`` strings.

    Returns ``None`` (rather than raising) when either value is unparseable,
    so callers can decide on a fallback.
    """
    try:
        e = datetime.strptime(normalize_time(entry), "%H:%M")
        x = datetime.strptime(normalize_time(exit_time), "%H:%M")
    except ValueError:
        return None
    return round((x - e).total_seconds() / 3600, 2)


def break_to_minutes(break_duration: Optional[str]) -> int:
    """Convert an ``HH:MM`` break string to whole minutes (0 if empty)."""
    if not break_duration or break_duration in ("00:00", ""):
        return 0
    try:
        hours, minutes = break_duration.split(":")
        return int(hours) * 60 + int(minutes)
    except (ValueError, IndexError):
        return 0


def _is_valid_hm(hours: str, minutes: str) -> bool:
    try:
        h, m = int(hours), int(minutes)
    except ValueError:
        return False
    return 0 <= h <= 23 and 0 <= m <= 59
