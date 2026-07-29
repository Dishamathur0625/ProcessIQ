import logging
from logging.handlers import RotatingFileHandler
import os
from backend.core.config import settings

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger with console and rotating file handlers.
    Creates a separate log file based on the logger name (e.g., 'api.log').
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(settings.LOG_LEVEL)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler
        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, f"{name}.log"),
            maxBytes=5*1024*1024, # 5 MB
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger
