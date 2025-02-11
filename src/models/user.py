from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime, timezone
import uuid

class Message(BaseModel):
    """Model representing a single message in a conversation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the message")
    content: str = Field(..., description="Content of the message")
    role: str = Field(..., description="Role of the sender (user or assistant)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Time the message was sent")

    @field_validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            raise ValueError('Role must be either "user" or "assistant"')
        return v

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat()
        }

class UserInput(BaseModel):
    message: str
    type: Optional[str] = "text"

class UserResponse(BaseModel):
    response: str
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

class ConversationContext(BaseModel):
    """Model for storing conversation context and state."""
    user_id: str = Field(..., description="Identifier for the user")
    memory: Dict[str, Any] = Field(default_factory=dict, description="Conversation memory store")
    session_id: Optional[str] = Field(default=None, description="Current session identifier")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences for this conversation")
    last_intent: Optional[str] = Field(default=None, description="Last detected conversation intent")
    last_entities: Dict[str, Any] = Field(default_factory=dict, description="Entities from last interaction")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def update_memory(self, key: str, value: Any) -> None:
        """Update conversation memory."""
        self.memory[key] = value
        self.updated_at = datetime.now(timezone.utc)

    def get_memory(self, key: str) -> Optional[Any]:
        """Retrieve value from conversation memory."""
        return self.memory.get(key)

    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update user preferences for this conversation."""
        self.preferences.update(preferences)
        self.updated_at = datetime.now(timezone.utc)

    def update_intent(self, intent: str) -> None:
        """Update last detected intent."""
        self.last_intent = intent
        self.updated_at = datetime.now(timezone.utc)

    def update_entities(self, entities: Dict[str, Any]) -> None:
        """Update last detected entities."""
        self.last_entities = entities
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "user_id": self.user_id,
            "memory": self.memory,
            "session_id": self.session_id,
            "preferences": self.preferences,
            "last_intent": self.last_intent,
            "last_entities": self.last_entities,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class Conversation(BaseModel):
    """Model for storing conversation history."""
    id: str = Field(..., description="Unique identifier for the conversation")
    user_id: str = Field(..., description="Identifier for the user")
    messages: List[Message] = Field(default_factory=list, description="List of messages in the conversation")
    context: ConversationContext = Field(..., description="Context for the conversation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date and time the conversation was created")
    last_active: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date and time of the last message")

    def add_message(self, content: str, role: str) -> None:
        """Add a new message to the conversation."""
        message = Message(
            content=content, 
            role=role,
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc)
        )
        self.messages.append(message)
        self.last_active = datetime.now(timezone.utc)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "context": self.context.to_dict() if self.context else None,
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