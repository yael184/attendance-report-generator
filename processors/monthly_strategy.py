import re
from typing import List
from core.models import AttendanceRow
from processors.base_strategy import IReportParsingStrategy
from logger_config import get_logger
from utils.time_handler import normalize_time, is_valid_time_format, is_valid_hours_value

logger = get_logger(__name__)

class MonthlyCardStrategy(IReportParsingStrategy):

    @property
    def report_type(self) -> str:
        return "TYPE_B"

    def identify(self, raw_text: str) -> bool:
        # OCR output shows variations of these words
        keywords = ["ימי עבודה", "שעות חודשיות", "שעת", "סה", "כניסה"]
        matches = sum(1 for word in keywords if word in raw_text)
        return matches >= 2

    def parse(self, raw_text: str) -> List[AttendanceRow]:
        logger.info("Starting Monthly Card parsing")
        parsed_rows = []
        
        # Updated patterns to support both dot and colon formats
        # Date pattern: matches 20/23, 4/1/23, 24/1123 (handling OCR errors)
        date_pattern = r"(\d{1,2}/\d{1,2}/?\d{0,4})"
        
        # Time pattern: matches both formats - 8:04, 8.04, 1103, 10:57, 10.57 etc
        # This captures any sequence with digit separators (: or .) or 3-4 consecutive digits
        time_pattern = r"(\d{1,2}[:\.]\d{2}|\d{3,4})"
        
        lines = raw_text.split('\n')
        logger.debug(f"Total lines to parse: {len(lines)}")
        
        for line_num, line in enumerate(lines):
            # Check if line has a date-like structure
            if not re.search(date_pattern, line):
                continue
                
            # Clean line from OCR noise like '|'
            clean_line = line.replace('|', ' ').strip()
            
            # Find all potential time/number values
            time_matches = re.findall(time_pattern, clean_line)
            date_match = re.search(date_pattern, clean_line)
            
            if not date_match or len(time_matches) < 3:
                continue
            
            logger.debug(f"Found record at line {line_num}: {clean_line[:50]}")
            logger.debug(f"Raw time matches: {time_matches}")
            
            # Filter and validate the matches
            valid_times = []
            valid_hours = None
            
            for match in time_matches:
                if is_valid_time_format(match):
                    valid_times.append(match)
                    logger.debug(f"Identified as time: {match}")
                elif is_valid_hours_value(match):
                    if valid_hours is None:  # Take only the first valid hours value
                        valid_hours = match
                        logger.debug(f"Identified as hours: {match}")
            
            # We need at least 2 times (entry and exit) and 1 hours value
            if len(valid_times) < 2:
                logger.debug(f"Not enough valid times found (got {len(valid_times)}, need 2)")
                continue
            
            logger.debug(f"Valid times: {valid_times}, Valid hours: {valid_hours}")
            
            entry_raw = valid_times[0]
            exit_raw = valid_times[1]
            total_raw = valid_hours if valid_hours else "0"
            
            logger.debug(f"Raw values - Date: {date_match.group(1)}, Entry: {entry_raw}, Exit: {exit_raw}, Total: {total_raw}")
            
            # Normalize times to HH:MM format
            entry_formatted = normalize_time(entry_raw)
            exit_formatted = normalize_time(exit_raw)
            logger.debug(f"Formatted times - Entry: {entry_formatted}, Exit: {exit_formatted}")
            
            # Convert total hours
            try:
                total_hours = float(total_raw.replace(',', '.'))
                # If value is > 24, assume it's in centminutes format (divide by 100)
                if total_hours > 24:
                    total_hours = total_hours / 100
            except (ValueError, AttributeError):
                total_hours = 0.0
                logger.warning(f"Could not parse total hours: {total_raw}")

            parsed_rows.append(AttendanceRow(
                date=date_match.group(1),
                day_of_week="", 
                entry_time=entry_formatted,
                exit_time=exit_formatted,
                total_hours=total_hours
            ))
        
        logger.info(f"Monthly Card parsing completed. Parsed {len(parsed_rows)} rows")
        return parsed_rows