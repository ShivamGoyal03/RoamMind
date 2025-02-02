import logging
from typing import Optional

def setup_logger(name: str, level: Optional[str] = "INFO") -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    
    # Set log level
    logger.setLevel(getattr(logging, level.upper()))
    
    # If no handlers are present, add one (prevents duplicate logs)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger