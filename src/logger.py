# logger.py
import logging
import os
from datetime import datetime

def setup_logger(feed_id: str = None) -> logging.Logger:
    """Set up logger with daily rotating file handler"""
    # Get the absolute path to the project root
    project_root = os.getcwd()
    
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

    # Create file handler
    if feed_id:
        try:
            # Extract mdb-id
            mdb_id = '-'.join(feed_id.split('-')[:2])
            
            # Create directory structure
            log_dir = os.path.join(project_root, 'logs', mdb_id)
            os.makedirs(log_dir, exist_ok=True)
            print(f"Created log directory: {log_dir}")
            
            # Create log file with today's date
            today = datetime.now().strftime('%Y%m%d')
            log_file = os.path.join(log_dir, f'bus_speeds_{today}.log')
            
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Error setting up log file: {str(e)}")
            raise

    return logger