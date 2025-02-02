from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class ExcursionSearchParams(BaseModel):
    """Parameters for excursion search."""
    location: str = Field(..., description="Location/city for the excursion")
    date: datetime = Field(..., description="Preferred date")
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
            "inclusions": self.inclusions,
            "meeting_point": self.meeting_point,
            "languages": self.languages
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
