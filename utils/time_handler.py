"""
Utility module for time format handling.
Supports both dot (6.30) and colon (18:30) formats.
"""

from logger_config import get_logger

logger = get_logger(__name__)


def normalize_time(time_str: str) -> str:
    """
    Convert any time format to standard HH:MM format.
    
    Supports:
    - 6.30 (dot format) -> 06:30
    - 6:30 (colon format) -> 06:30
    - 630 (no separator) -> 06:30
    - 18.30 (dot format) -> 18:30
    - 18:30 (colon format) -> 18:30
    - 1830 (no separator) -> 18:30
    
    Args:
        time_str: Time string in any supported format
        
    Returns:
        str: Time in HH:MM format, or original if invalid
    """
    if not time_str:
        return time_str
    
    try:
        # Remove any spaces
        time_str = time_str.strip()
        
        # Replace dot with colon for normalization
        time_str = time_str.replace('.', ':')
        
        # If already has colon, validate and pad
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                hours, minutes = parts
                hours = hours.zfill(2)
                minutes = minutes.zfill(2)
                
                # Validate hours and minutes
                h = int(hours)
                m = int(minutes)
                if 0 <= h <= 23 and 0 <= m <= 59:
                    logger.debug(f"Normalized time: {time_str} -> {hours}:{minutes}")
                    return f"{hours}:{minutes}"
        else:
            # No separator - assume it's a 3 or 4 digit number
            digits = ''.join(c for c in time_str if c.isdigit())
            
            if len(digits) == 3:
                # e.g., "630" -> "06:30"
                hours = digits[0].zfill(2)
                minutes = digits[1:3]
            elif len(digits) == 4:
                # e.g., "1830" -> "18:30"
                hours = digits[0:2]
                minutes = digits[2:4]
            else:
                logger.warning(f"Invalid time format: {time_str}")
                return time_str
            
            h = int(hours)
            m = int(minutes)
            if 0 <= h <= 23 and 0 <= m <= 59:
                logger.debug(f"Normalized time: {time_str} -> {hours}:{minutes}")
                return f"{hours}:{minutes}"
    
    except (ValueError, AttributeError) as e:
        logger.warning(f"Failed to normalize time '{time_str}': {e}")
    
    return time_str


def is_valid_time_format(value: str) -> bool:
    """
    Check if a value looks like a time (to distinguish from total hours).
    
    Args:
        value: String value to check
        
    Returns:
        bool: True if value appears to be in time format
    """
    if not value:
        return False
    
    # Replace dot with colon for checking
    check_val = value.replace('.', ':')
    
    # Time format check: contains colon or is 3-4 digits
    if ':' in check_val:
        parts = check_val.split(':')
        if len(parts) == 2:
            try:
                h = int(parts[0])
                m = int(parts[1])
                # Both hour and minute parts must be valid
                return 0 <= h <= 23 and 0 <= m <= 59 and len(parts[1]) == 2
            except ValueError:
                return False
    
    # Check if it's a 3-4 digit number without decimals
    digits = ''.join(c for c in value if c.isdigit())
    if len(digits) in [3, 4] and '.' not in value:
        try:
            if len(digits) == 3:
                h, m = int(digits[0]), int(digits[1:3])
            else:
                h, m = int(digits[0:2]), int(digits[2:4])
            return 0 <= h <= 23 and 0 <= m <= 59
        except ValueError:
            return False
    
    return False


def is_valid_hours_value(value: str) -> bool:
    """
    Check if a value looks like a total hours value.
    
    Args:
        value: String value to check
        
    Returns:
        bool: True if value appears to be total hours
    """
    if not value:
        return False
    
    try:
        # Hours can be decimal (like 6.50) or integer (like 350 for minutes)
        val = float(value.replace(',', '.'))
        # Valid hours: 0 to 24, or 0 to 1440 (minutes)
        return 0 <= val <= 1440
    except ValueError:
        return False
