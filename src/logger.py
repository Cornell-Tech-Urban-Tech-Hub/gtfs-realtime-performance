# logger.py
import logging
import os
from datetime import datetime

def setup_logger() -> logging.Logger:
    """Set up logger with daily rotating file handler"""
    # Create base logs directory first
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger('bus_speed_processor')
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        # Create log file with today's date
        today = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join('logs', f'bus_speeds_{today}.log')
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Test write to log file
        logger.info("Logger initialized")
        
    except Exception as e:
        print(f"Error setting up log file: {str(e)}")
        raise

    return logger