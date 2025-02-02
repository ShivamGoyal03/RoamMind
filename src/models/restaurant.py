from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class MenuItem(BaseModel):
    """Individual menu item model."""
    id: str
    name: str
    description: str
    price: float
    category: str
    dietary_info: Optional[List[str]] = []
    is_available: bool = True

class MenuCategory(BaseModel):
    """Menu category containing items."""
    name: str
    items: List[MenuItem]

class Menu(BaseModel):
    """Complete restaurant menu."""
    restaurant_id: str
    restaurant_name: str
    categories: List[MenuCategory]
    last_updated: datetime

class Review(BaseModel):
    """Restaurant review model."""
    id: str
    restaurant_id: str
    author: str
    rating: float
    comment: str
    date: datetime

class Restaurant(BaseModel):
    """Restaurant model."""
    id: str
    name: str
    cuisine_type: List[str]
    price_range: str
    location: str
    rating: float
    review_count: int
    opening_hours: Dict[str, str]
    phone: str
    website: Optional[str] = None
    menu: Optional[Menu] = None
    reviews: Optional[List[Review]] = []

    def __init__(self, **data):
        logger.debug(f"Creating Restaurant instance with data: {data}")
        super().__init__(**data)

class RestaurantSearchParams(BaseModel):
    """Parameters for restaurant search."""
    cuisine: Optional[List[str]] = None
    location: Optional[str] = None
    price_range: Optional[str] = None
    min_rating: Optional[float] = None

class RestaurantReview(BaseModel):
    """Model representing a restaurant review."""
    id: str
    rating: float
    review_text: str
    author: str
    date: datetime
    dining_date: datetime
    helpful_votes: int = 0
    response: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "rating": self.rating,
            "review_text": self.review_text,
            "author": self.author,
            "date": self.date.isoformat(),
            "dining_date": self.dining_date.isoformat(),
            "helpful_votes": self.helpful_votes,
            "response": self.response
        } 