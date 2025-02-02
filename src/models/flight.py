from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class FlightSearchParams(BaseModel):
    """Parameters for flight search."""
    origin: str
    destination: str
    departure_date: datetime
    return_date: Optional[datetime] = None
    passengers: int = 1
    cabin_class: Optional[str] = None
    max_price: Optional[float] = None
    preferred_airlines: Optional[List[str]] = None 
    direct_flights_only: bool = False

class Flight(BaseModel):
    """Model representing a flight."""
    id: str
    airline: str = Field(..., min_length=2, max_length=50)
    flight_number: str = Field(..., min_length=2, max_length=10) 
    departure_airport: str = Field(..., min_length=3, max_length=10) 
    arrival_airport: str = Field(..., min_length=3, max_length=10) 
    departure_time: datetime
    arrival_time: datetime
    duration: int  
    price: float
    available_seats: int
    aircraft_type: Optional[str] = None 
    cabin_class: str
    baggage_allowance: str
    status: str = "Scheduled"
    gate: Optional[str] = None
    terminal: Optional[str] = None
    additional_info: Optional[str] = None
    amenities: Optional[Dict[str, bool]] = None
    meal_service: Optional[bool] = None

    def to_dict(self) -> Dict:
        """Convert flight object to dictionary."""
        logger.debug(f"Converting flight {self.flight_number} to dict")
        return self.model_dump(exclude_unset=True) 