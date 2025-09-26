"""
Shared logging configuration and utilities
"""
import logging
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger with both file and console handlers
    
    Args:
        name (str): Logger name
        log_file (str, optional): Log file path (default: logs/{name}.log)
        level: Logging level (default: INFO)
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # File handler
    if not log_file:
        log_file = f'logs/{name.lower()}.log'
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    return logger

def setup_main_logger():
    """Set up the main application logger"""
    return setup_logger('jordan_scraper', 'logs/main.log')

class LoggingMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self):
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = setup_logger(self.__class__.__name__)
        return self._logger

def log_scraping_session(website, status, products_count, notes="", logger=None):
    """
    Helper function to log scraping sessions
    
    Args:
        website (str): Website name
        status (str): Session status
        products_count (int): Number of products scraped
        notes (str): Additional notes
        logger: Logger instance to use
    """
    if not logger:
        logger = setup_main_logger()
    
    session_info = {
        'website': website,
        'status': status,
        'products_count': products_count,
        'timestamp': datetime.now().isoformat(),
        'notes': notes
    }
    
    logger.info(f"Scraping Session: {session_info}")
    return session_info