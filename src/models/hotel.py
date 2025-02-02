from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator

class HotelSearchParams(BaseModel):
    """Parameters for hotel search."""
    location: str = Field(..., description="City or region of the hotel")
    check_in: datetime = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out: datetime = Field(..., description="Check-out date (YYYY-MM-DD)")
    guests: int = Field(default=1, ge=1, description="Number of guests (minimum 1)")
    rooms: int = Field(default=1, ge=1, description="Number of rooms (minimum 1)")
    max_price: Optional[float] = Field(None, description="Maximum price per night")
    amenities: List[str] = Field(default_factory=list, description="List of required amenities")
    star_rating: Optional[int] = Field(None, ge=1, le=5, description="Minimum star rating (1-5)")
    room_type: Optional[str] = Field(None, description="Preferred room type (e.g., 'Standard', 'Deluxe')")

class Room(BaseModel):
    """Model representing a hotel room."""
    id: str = Field(..., description="Unique room identifier")
    type: str = Field(..., description="Room type (e.g., Standard, Deluxe)")
    description: str
    capacity: int = Field(..., ge=1, description="Maximum number of guests (minimum 1)")
    price_per_night: float = Field(..., gt=0, description="Price per night (must be greater than 0)")
    amenities: List[str] = Field(default_factory=list, description="List of room amenities")
    available: bool = True
    bed_type: str = Field(..., description="Type of bed (e.g., 'King', 'Queen')")
    view: Optional[str] = Field(None, description="Room view (e.g., 'City', 'Ocean')")


class Hotel(BaseModel):
    """Model representing a hotel."""
    id: str = Field(..., description="Unique hotel identifier")
    name: str = Field(..., min_length=2, max_length=100, description="Hotel name")
    description: str = Field(..., description="Hotel description")
    location: str = Field(..., min_length=2, max_length=100, description="City or region of the hotel")
    star_rating: float = Field(..., ge=1, le=5, description="Star rating (1-5)")
    amenities: List[str] = Field(default_factory=list, description="List of hotel amenities")
    rooms: List[Room] = Field(default_factory=list, description="List of available rooms")
    address: str = Field(..., min_length=10, max_length=200, description="Hotel address")
    latitude: float
    longitude: float
    check_in_time: str = "15:00"
    check_out_time: str = "11:00"
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    rating: Optional[float] = Field(None, ge=0, le=5, description="User rating (0-5)")
    review_count: int = 0

    def to_dict(self) -> Dict:
        return self.model_dump(exclude_unset=True)