# logger.py
import logging
import os
from datetime import datetime

def setup_logger(log_dir="logs"):
    """Set up application-wide logger with daily log files"""
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger('bus_speed_processor')
    if logger.handlers:  # Return if logger is already configured
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Daily log file with today's date
    today = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f'bus_speeds_{today}.log')
    
    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()
    
    # Create formatter - removed route_id
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Starting new processing session")
    
    return logger