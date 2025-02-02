import logging

logger = logging.getLogger(__name__)

class BookingError(Exception):
    """Raised when there's an error during booking process."""
    def __init__(self, message: str):
        logger.error(f"Booking error: {message}")
        super().__init__(message)

class ExcursionNotFoundError(Exception):
    """Raised when an excursion cannot be found."""
    def __init__(self, excursion_id: str):
        message = f"Excursion not found: {excursion_id}"
        logger.error(message)
        super().__init__(message)

class InvalidDateError(Exception):
    """Raised when an invalid date is provided."""
    def __init__(self, date_str: str):
        message = f"Invalid date provided: {date_str}"
        logger.error(message)
        super().__init__(message)

class BookingNotFoundError(Exception):
    """Raised when a booking reference cannot be found."""
    def __init__(self, reference: str):
        message = f"Booking not found: {reference}"
        logger.error(message)
        super().__init__(message)

class CancellationError(Exception):
    """Raised when there's an error during cancellation process."""
    def __init__(self, booking_ref: str, reason: str):
        message = f"Error cancelling booking {booking_ref}: {reason}"
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

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    def __init__(self, message: str):
        logger.error(f"Authentication error: {message}")
        super().__init__(message)

class ValidationError(Exception):
    """Raised when input validation fails."""
    def __init__(self, errors: dict):
        message = f"Validation error: {str(errors)}"
        logger.error(message)
        self.errors = errors
        super().__init__(message)

class ServiceUnavailableError(Exception):
    """Raised when an external service is unavailable."""
    def __init__(self, service_name: str):
        message = f"Service unavailable: {service_name}"
        logger.error(message)
        super().__init__(message)

class PaymentError(Exception):
    """Raised when there's an error processing payment."""
    def __init__(self, message: str, payment_id: str = None):
        log_message = f"Payment error: {message}"
        if payment_id:
            log_message += f" (Payment ID: {payment_id})"
        logger.error(log_message)
        super().__init__(message)

class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    def __init__(self, limit: int, reset_time: str):
        message = f"Rate limit exceeded. Limit: {limit}, Reset at: {reset_time}"
        logger.error(message)
        super().__init__(message)

class DatabaseError(Exception):
    """Raised when there's an error with database operations."""
    def __init__(self, operation: str, details: str):
        message = f"Database error during {operation}: {details}"
        logger.error(message)
        super().__init__(message)

class ConfigurationError(Exception):
    """Raised when there's an error in configuration."""
    def __init__(self, config_key: str, details: str):
        message = f"Configuration error for {config_key}: {details}"
        logger.error(message)
        super().__init__(message) 