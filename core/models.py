from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class AttendanceRow:
    date: str
    day_of_week: str
    entry_time: str
    exit_time: str
    total_hours: float
    location: Optional[str] = None
    break_duration: Optional[str] = "00:00"
    # TYPE_B (Monthly Card) optional overtime fields
    break_minutes: Optional[int] = None
    overtime_125_hours: Optional[float] = None
    overtime_150_hours: Optional[float] = None
    overtime_shabbat_hours: Optional[float] = None
    raw_metadata: dict = field(default_factory=dict)


@dataclass
class AttendanceReport:
    report_type: str
    employee_name: Optional[str]
    month_year: str
    rows: Tuple[AttendanceRow, ...]
    total_monthly_hours: float
    total_days: int


# Keep ReportData as an alias for backward compatibility
ReportData = AttendanceReport