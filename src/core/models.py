from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid

class Message(BaseModel):
    """Model for storing conversation messages."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat()
        }

class TravelPreferences(BaseModel):
    """Model for user travel preferences."""
    budget: Optional[float] = None
    preferred_airlines: List[str] = []
    seat_preference: Optional[str] = None
    meal_preference: Optional[str] = None
    accessibility_needs: List[str] = []
    hotel_preferences: Dict[str, Any] = {}
    dining_preferences: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict:
        return {
            "budget": self.budget,
            "preferred_airlines": self.preferred_airlines,
            "seat_preference": self.seat_preference,
            "meal_preference": self.meal_preference,
            "accessibility_needs": self.accessibility_needs,
            "hotel_preferences": self.hotel_preferences,
            "dining_preferences": self.dining_preferences
        }

class ConversationContext(BaseModel):
    """Model for conversation context."""
    user_id: str
    memory: Dict[str, Any] = {}
    session_id: Optional[str] = None
    preferences: Dict[str, Any] = {}
    last_intent: Optional[str] = None
    last_entities: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "memory": self.memory,
            "session_id": self.session_id,
            "preferences": self.preferences,
            "last_intent": self.last_intent,
            "last_entities": self.last_entities
        }

class Conversation(BaseModel):
    """Model for storing conversation history."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    context: ConversationContext
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True
    
    def add_message(self, content: str, role: str):
        message = Message(content=content, role=role)
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)
        
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "context": self.context.to_dict(),
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "active": self.active
        }

class User(BaseModel):
    """Model for user information."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    hashed_password: str
    full_name: str
    preferences: TravelPreferences = Field(default_factory=TravelPreferences)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "preferences": self.preferences.to_dict(),
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }