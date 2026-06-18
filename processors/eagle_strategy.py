import re
from typing import List
from core.models import AttendanceRow
from processors.base_strategy import IReportParsingStrategy
from logger_config import get_logger
from utils.time_handler import normalize_time

logger = get_logger(__name__)

class EagleReportStrategy(IReportParsingStrategy):

    @property
    def report_type(self) -> str:
        return "TYPE_A"

    def identify(self, raw_text: str) -> bool:
        """Checks if the report belongs to 'Eagle' based on the company name."""
        return "הנשר" in raw_text or "גליליון" in raw_text

    def parse(self, raw_text: str) -> List[AttendanceRow]:
        """
        Parses the text to extract date, times, and total hours.
        Supports both dot (6.30) and colon (18:30) time formats.
        """
        logger.info("Starting Eagle Report parsing")
        parsed_rows = []
        
        # Regex patterns for specific fields
        # Date: DD/MM/YYYY
        date_pattern = r"(\d{2}/\d{2}/\d{4})" 
        # Time: HH:MM, HH.MM, or HHMM format
        time_pattern = r"(\d{1,2}[:\.]\d{2}|\d{3,4})"
        # Decimal numbers (for total hours): 6.50
        decimal_pattern = r"(\d+(?:[.,]\d{2})?)" 

        lines = raw_text.split('\n')
        logger.debug(f"Total lines to parse: {len(lines)}")
        
        # Temporary storage for multi-line extraction
        current_date = None
        
        for line_num, line in enumerate(lines):
            # 1. Look for a date in the line
            date_match = re.search(date_pattern, line)
            if date_match:
                current_date = date_match.group(1)
                logger.debug(f"Found date: {current_date}")
                
            # 2. If we have a date, look for time stamps in the same or subsequent lines
            times = re.findall(time_pattern, line)
            
            # In this report, entry/exit often appear together or near the date
            if current_date and len(times) >= 2:
                # Based on the sample: Entry is often the 2nd time, Exit the 1st (due to RTL/LTR issues)
                # We need to ensure entry_time < exit_time after processing
                t1, t2 = times[0], times[1]
                
                # Normalize both times to HH:MM format
                t1_normalized = normalize_time(t1)
                t2_normalized = normalize_time(t2)
                
                # Simple logic to distinguish entry/exit
                entry = min(t1_normalized, t2_normalized)
                exit_time = max(t1_normalized, t2_normalized)
                
                logger.debug(f"Found times - Raw: {t1}, {t2} -> Normalized: {t1_normalized}, {t2_normalized} -> Entry: {entry}, Exit: {exit_time}")

                # 3. Look for the total hours (usually a decimal like 6.50)
                hours_match = re.search(decimal_pattern, line)
                total_h = 0.0
                if hours_match:
                    try:
                        total_h = float(hours_match.group(1).replace(',', '.'))
                    except ValueError:
                        logger.warning(f"Could not parse hours: {hours_match.group(1)}")
                
                logger.debug(f"Total hours: {total_h}")

                parsed_rows.append(AttendanceRow(
                    date=current_date,
                    day_of_week="", # Can be inferred from the date
                    entry_time=entry,
                    exit_time=exit_time,
                    total_hours=total_h,
                    location="גליליון" # Identified from the text 
                ))
                
                # Reset for next record
                current_date = None

        logger.info(f"Eagle Report parsing completed. Parsed {len(parsed_rows)} rows")
        return parsed_rows