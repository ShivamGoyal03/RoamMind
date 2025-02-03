import logging

logger = logging.getLogger(__name__)

class ExcursionNotFoundError(Exception):
    """Raised when an excursion cannot be found."""
    def __init__(self, excursion_id: str):
        message = f"Excursion not found: {excursion_id}"
        logger.error(message)
        super().__init__(message)

class FlightNotFoundError(Exception):
    """Raised when a flight cannot be found."""
    def __init__(self, flight_id: str):
        message = f"Flight not found: {flight_id}"
        logger.error(message)
        super().__init__(message)

class HotelNotFoundError(Exception):
    """Raised when a hotel cannot be found."""
    def __init__(self, hotel_id: str):
        message = f"Hotel not found: {hotel_id}"
        logger.error(message)
        super().__init__(message)

class RestaurantNotFoundError(Exception):
    """Raised when a restaurant cannot be found."""
    def __init__(self, restaurant_id: str):
        message = f"Restaurant not found: {restaurant_id}"
        logger.error(message)
        super().__init__(message)

class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class APIConnectionError(Exception):
    """Exception raised for API connection errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class DatabaseError(Exception):
    """Exception raised for database-related errors."""
    def __init__(self, operation: str, message: str):
        super().__init__(message)
        self.operation = operation
        self.message = message

    def __str__(self):
        return f"DatabaseError during {self.operation}: {self.message}"

class CosmosClientError(Exception):
    """Exception raised for Cosmos DB client errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
    
    def __str__(self):
        return f"CosmosClientError: {self.message}"