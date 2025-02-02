from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class ExcursionSearchParams(BaseModel):
    """Parameters for excursion search."""
    location: str = Field(..., description="Location/city for the excursion")
    date: datetime = Field(..., description="Preferred date")
    participants: int = Field(default=1, description="Number of participants")
    category: Optional[str] = Field(None, description="Type of activity")
    max_price: Optional[float] = Field(None, description="Maximum price per person")
    duration: Optional[float] = Field(None, description="Preferred duration in hours")

class Excursion(BaseModel):
    """Model representing an excursion or activity."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name of the excursion")
    description: str = Field(..., description="Detailed description")
    location: str = Field(..., description="Location where it takes place")
    duration: float = Field(..., description="Duration in hours")
    price: float = Field(..., description="Price per person")
    category: str = Field(..., description="Category of activity")
    max_participants: int = Field(..., description="Maximum number of participants")
    available_dates: List[datetime] = Field(default_factory=list)
    inclusions: List[str] = Field(default_factory=list, description="What's included")
    meeting_point: str = Field(..., description="Meeting point details")
    languages: List[str] = Field(default_factory=list, description="Available languages")
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "duration": self.duration,
            "price": self.price,
            "category": self.category,
            "max_participants": self.max_participants,
            "available_dates": [d.isoformat() for d in self.available_dates],
            "inclusions": self.inclusions,
            "meeting_point": self.meeting_point,
            "languages": self.languages
        }

class ExcursionBooking(BaseModel):
    """Model representing an excursion booking."""
    reference: str = Field(..., description="Unique booking reference")
    excursion: Excursion = Field(..., description="Booked excursion details")
    date: datetime = Field(..., description="Booked date")
    participants: int = Field(..., description="Number of participants")
    total_price: float = Field(..., description="Total booking price")
    customer_name: str = Field(..., description="Customer name")
    customer_email: str = Field(..., description="Customer email")
    status: str = Field(default="confirmed", description="Booking status")
    special_requests: Optional[str] = Field(None, description="Special requests")
    booking_date: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "reference": self.reference,
            "excursion": self.excursion.to_dict(),
            "date": self.date.isoformat(),
            "participants": self.participants,
            "total_price": self.total_price,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "status": self.status,
            "special_requests": self.special_requests,
            "booking_date": self.booking_date.isoformat()
        }

class ExcursionCancellation(BaseModel):
    """Model representing a cancelled excursion booking."""
    booking_reference: str = Field(..., description="Reference of the cancelled booking")
    cancellation_date: datetime = Field(default_factory=datetime.now)
    refund_amount: float = Field(..., description="Amount to be refunded")
    reason: Optional[str] = Field(None, description="Reason for cancellation")
    
    def to_dict(self) -> Dict:
        """Convert the cancellation to a dictionary."""
        return {
            "booking_reference": self.booking_reference,
            "cancellation_date": self.cancellation_date.isoformat(),
            "refund_amount": self.refund_amount,
            "reason": self.reason
        }

class ActivityRecommendation(BaseModel):
    """Model representing a recommended activity."""
    name: str = Field(..., description="Name of the recommended activity")
    description: str = Field(..., description="Description of the activity")
    match_score: float = Field(..., description="Match score percentage")
    excursion: Excursion = Field(..., description="The recommended excursion")
    
    def to_dict(self) -> Dict:
        """Convert the recommendation to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "match_score": self.match_score,
            "excursion": self.excursion.to_dict()
        } 