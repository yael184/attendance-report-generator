import logging
import os
from datetime import datetime

def setup_logger(name=None, log_file="logs/app.log"):
    """
    Configure and return a logger with both file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Path where logs will be saved
    
    Returns:
        logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name or "attendance_app")
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers if logger is reused
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter with detailed information
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler - logs all messages (DEBUG and above)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler - logs INFO and above for user visibility
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        fmt='%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logger("attendance_app")

def get_logger(module_name=None):
    """
    Get a logger instance for a specific module.
    
    Args:
        module_name: Name of the module requesting the logger
    
    Returns:
        logger: Logger instance
    """
    if module_name:
        return logging.getLogger(f"attendance_app.{module_name}")
    return logger
