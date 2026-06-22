"""TYPE_A parser — "Eagle" (הנשר) attendance reports."""

from __future__ import annotations

import re
from typing import Dict, Optional

from ...domain.models import AttendanceRow
from ...domain.time_utils import normalize_time
from .base_parser import BaseReportParser
from .factory import ParserFactory

_DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")
_TIME_RE = re.compile(r"(\d{1,2}[:.]\d{2}|\d{3,4})")
_DECIMAL_RE = re.compile(r"(\d+(?:[.,]\d{2})?)")


@ParserFactory.register
class EagleReportParser(BaseReportParser):
    """Parses Eagle reports where a date line is followed by time stamps."""

    report_type = "TYPE_A"

    def matches(self, raw_text: str) -> bool:
        return "הנשר" in raw_text or "גליליון" in raw_text

    def _parse_line(
        self, line: str, state: Dict[str, object]
    ) -> Optional[AttendanceRow]:
        date_match = _DATE_RE.search(line)
        # Remove the date span so its year (e.g. 2024) is not read as a time.
        scan_text = line[: date_match.start()] + line[date_match.end() :] if date_match else line
        if date_match:
            state["current_date"] = date_match.group(1)

        current_date = state.get("current_date")
        if not current_date:
            return None

        times = _TIME_RE.findall(scan_text)
        if len(times) < 2:
            return None

        t1, t2 = normalize_time(times[0]), normalize_time(times[1])
        entry, exit_time = min(t1, t2), max(t1, t2)

        total_hours = 0.0
        hours_match = _DECIMAL_RE.search(scan_text)
        if hours_match:
            try:
                total_hours = float(hours_match.group(1).replace(",", "."))
            except ValueError:
                total_hours = 0.0

        # Record consumed — clear the carried date for the next record.
        state.pop("current_date", None)

        return AttendanceRow(
            date=str(current_date),
            day_of_week="",
            entry_time=entry,
            exit_time=exit_time,
            total_hours=total_hours,
            location="גליליון",
        )
