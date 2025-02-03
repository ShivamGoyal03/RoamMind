from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
import uuid

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    role: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat()
        }

class UserInput(BaseModel):
    message: str = Field(..., description="User's message")

class UserResponse(BaseModel):
    response: str = Field(..., description="System's response")
    success: bool = Field(..., description="Indicates if the request was successful")
    data: Optional[Dict] = Field(None, description="Additional data associated with the response")
    suggestions: List[str] = Field(default_factory=list, description="List of suggestions")

class Conversation(BaseModel):
    id: str = Field(..., description="Unique identifier for the conversation")
    user_id: str = Field(..., description="Identifier for the user")
    messages: List[Message] = Field(default_factory=list, description="List of messages in the conversation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date and time the conversation was created")
    last_active: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date and time of the last message")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "messages": [msg.to_dict() for msg in self.messages], #Convert messages to dict
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr = Field(..., description="User's email address") #Email validation
    hashed_password: str = Field(..., description="Hashed password")
    full_name: str = Field(..., description="User's full name")
    preferences: Optional[Dict[str,Any]] = None #Allow flexibility for preferences
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Account creation timestamp")
    last_login: Optional[datetime] = None


    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }