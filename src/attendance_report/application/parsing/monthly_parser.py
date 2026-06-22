"""TYPE_B parser — "Monthly Card" (כרטיס חודשי) attendance reports."""

from __future__ import annotations

import re
from typing import Dict, Optional

from ...domain.models import AttendanceRow
from ...domain.time_utils import (
    is_valid_hours_value,
    is_valid_time_format,
    normalize_time,
)
from .base_parser import BaseReportParser
from .factory import ParserFactory

_DATE_RE = re.compile(r"(\d{1,2}/\d{1,2}/?\d{0,4})")
_TIME_RE = re.compile(r"(\d{1,2}[:.]\d{2}|\d{3,4})")
_KEYWORDS = ("ימי עבודה", "שעות חודשיות", "שעת", "סה", "כניסה")


@ParserFactory.register
class MonthlyCardParser(BaseReportParser):
    """Parses monthly-card reports where each row line holds date + times."""

    report_type = "TYPE_B"

    def matches(self, raw_text: str) -> bool:
        return sum(1 for word in _KEYWORDS if word in raw_text) >= 2

    def _parse_line(
        self, line: str, state: Dict[str, object]
    ) -> Optional[AttendanceRow]:
        date_match = _DATE_RE.search(line)
        if not date_match:
            return None

        # Drop the date span (and OCR pipe noise) so a 4-digit year is not
        # mistaken for a time value.
        without_date = line[: date_match.start()] + line[date_match.end() :]
        clean_line = without_date.replace("|", " ").strip()
        time_matches = _TIME_RE.findall(clean_line)
        if len(time_matches) < 3:
            return None

        valid_times = []
        valid_hours: Optional[str] = None
        for match in time_matches:
            if is_valid_time_format(match):
                valid_times.append(match)
            elif valid_hours is None and is_valid_hours_value(match):
                valid_hours = match

        if len(valid_times) < 2:
            return None

        total_hours = 0.0
        if valid_hours is not None:
            try:
                total_hours = float(valid_hours.replace(",", "."))
                if total_hours > 24:  # OCR centi-minutes (e.g. 850 -> 8.5)
                    total_hours /= 100
            except ValueError:
                total_hours = 0.0

        return AttendanceRow(
            date=date_match.group(1),
            day_of_week="",
            entry_time=normalize_time(valid_times[0]),
            exit_time=normalize_time(valid_times[1]),
            total_hours=total_hours,
        )
