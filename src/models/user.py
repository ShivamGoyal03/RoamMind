from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

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
    messages: List[Dict] = Field(default_factory=list, description="List of messages in the conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date and time the conversation was created")
    last_active: datetime = Field(default_factory=datetime.utcnow, description="Date and time of the last message")

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }