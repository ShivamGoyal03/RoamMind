from datetime import datetime
from typing import Optional
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.
    Supports multiple common date formats.
    
    Args:
        date_str: String representation of date/time
        
    Returns:
        datetime object if parsing successful, None otherwise
    """
    formats = [
        "%Y-%m-%d",           # 2024-03-15
        "%d/%m/%Y",           # 15/03/2024
        "%m/%d/%Y",           # 03/15/2024
        "%B %d, %Y",          # March 15, 2024
        "%d %B %Y",           # 15 March 2024
        "%Y-%m-%d %H:%M",     # 2024-03-15 14:30
        "%d/%m/%Y %H:%M",     # 15/03/2024 14:30
        "%m/%d/%Y %H:%M",     # 03/15/2024 14:30
        "%Y-%m-%dT%H:%M:%S",  # 2024-03-15T14:30:00
        "%Y-%m-%dT%H:%M:%SZ"  # 2024-03-15T14:30:00Z
    ]
    
    for fmt in formats:
        try:
            logger.debug(f"Attempting to parse date '{date_str}' with format '{fmt}'")
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Failed to parse date string: {date_str}")
    return None 