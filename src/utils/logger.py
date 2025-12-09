"""
Logging utilities for the trading bot
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class Logger:
    """Custom logger for the trading bot"""
    
    def __init__(self, name: str, log_file: Optional[str] = None, level: str = "INFO"):
        """
        Initialize logger
        
        Args:
            name: Logger name
            log_file: Path to log file (optional)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if log file specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info)


def get_logger(name: str, config: Optional[dict] = None) -> Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        config: Configuration dictionary with 'level' and 'file' keys
        
    Returns:
        Logger instance
    """
    if config is None:
        config = {}
    
    level = config.get('level', 'INFO')
    log_file = config.get('file', f'logs/{name}_{datetime.now().strftime("%Y%m%d")}.log')
    
    return Logger(name, log_file, level)
