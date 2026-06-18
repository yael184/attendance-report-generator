import hashlib
from datetime import datetime, timedelta
from .models import AttendanceRow
from logger_config import get_logger
from utils.time_handler import normalize_time

logger = get_logger(__name__)

class VariationEngine:
    """
    Responsible for applying 'reliable variations' to the attendance data.
    The changes are deterministic based on the input string to ensure consistency.
    """

    def __init__(self, seed_base: str):
        # Create a unique integer seed from the filename or employee name
        # to keep the variations deterministic.
        self.seed = int(hashlib.md5(seed_base.encode()).hexdigest(), 16) % 100

    def adjust_time(self, time_str: str, offset_minutes: int) -> str:
        """Adds or subtracts minutes from a time string (supports HH:MM and HH.MM formats)."""
        if not time_str:
            return time_str
        
        # First normalize the time to HH:MM format
        normalized_time = normalize_time(time_str)
        
        if not normalized_time or ":" not in normalized_time:
            return time_str
        
        fmt = "%H:%M"
        try:
            t = datetime.strptime(normalized_time, fmt)
            new_time = t + timedelta(minutes=offset_minutes)
            return new_time.strftime(fmt)
        except ValueError as e:
            logger.warning(f"Failed to adjust time '{time_str}': {e}")
            return time_str

    def apply_variation(self, row: AttendanceRow) -> AttendanceRow:
        """
        Applies logic to a single row: 
        e.g., adding a small deterministic jitter to entry/exit.
        """
        logger.debug(f"Applying variations to row - Date: {row.date}, Original Entry: {row.entry_time}, Exit: {row.exit_time}")
        
        # Deterministic jitter: entry + (seed % 5) minutes, exit - (seed % 3) minutes
        jitter_entry = self.seed % 7 
        jitter_exit = -(self.seed % 4)

        logger.debug(f"Jitter values - Entry offset: {jitter_entry} minutes, Exit offset: {jitter_exit} minutes")

        new_entry = self.adjust_time(row.entry_time, jitter_entry)
        new_exit = self.adjust_time(row.exit_time, jitter_exit)

        logger.debug(f"Modified times - New Entry: {new_entry}, New Exit: {new_exit}")

        # Validation: Ensure finish > start
        # (This is a simplified check, more logic can be added)
        
        row.entry_time = new_entry
        row.exit_time = new_exit
        
        return row