import logging
from typing import Dict, Optional, Any, List
import uuid
from datetime import datetime, timezone, timedelta
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..core.config import get_settings
from ..models import Conversation, ConversationContext
from ..infrastructure import AzureOpenAIService
from ..skills import (
    ExcursionSkill,
    RestaurantSkill,
    HotelSkill,
    FlightSkill
)

# In-memory session storage with last activity timestamp
session_conversations: Dict[str, tuple[Conversation, datetime]] = {}

# Session timeout (30 minutes)
SESSION_TIMEOUT = timedelta(minutes=30)

class Orchestrator:
    """Orchestrator for coordinating between different agents and managing conversations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Obtain configuration settings
        settings = get_settings()
        
        # Initialize the Kernel
        self.kernel = Kernel(endpoint=settings.azure_openai_endpoint, api_key=settings.azure_openai_api_key)
        
        # Initialize services and skills
        self.azure_service = AzureOpenAIService(self.kernel)
        self.excursion_skill = ExcursionSkill(self.kernel)
        self.restaurant_skill = RestaurantSkill(self.kernel)
        self.hotel_skill = HotelSkill(self.kernel)
        self.flight_skill = FlightSkill(self.kernel)

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        current_time = datetime.now(timezone.utc)
        expired_sessions = [
            session_id for session_id, (_, last_active) in session_conversations.items()
            if current_time - last_active > SESSION_TIMEOUT
        ]
        for session_id in expired_sessions:
            self.cleanup_session(session_id)

    async def save_conversation_state(self, conversation_id: str, message: str, role: str) -> None:
        """Save conversation state in memory with timestamp."""
        try:
            self._cleanup_expired_sessions()
            
            if conversation_id not in session_conversations:
                context = ConversationContext(user_id=str(uuid.uuid4()))
                conversation = Conversation(
                    id=conversation_id,
                    user_id=context.user_id,
                    context=context,
                    messages=[]
                )
                session_conversations[conversation_id] = (conversation, datetime.now(timezone.utc))
            
            conversation, _ = session_conversations[conversation_id]
            conversation.add_message(content=message, role=role)
            session_conversations[conversation_id] = (conversation, datetime.now(timezone.utc))
            
        except Exception as e:
            self.logger.error(f"Error saving conversation state: {str(e)}")
            raise

    async def load_conversation_history(self, conversation_id: str) -> Optional[Conversation]:
        """Load conversation history from memory."""
        return session_conversations.get(conversation_id)

    async def process_user_input(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """Process user input and maintain conversation history."""
        try:
            # Save user message
            await self.save_conversation_state(conversation_id, message, "user")
            
            # Process message
            lowered = message.lower()
            response = ""
            skill_invoked = False
            context = KernelArguments({"input": message})

            if "excursion" in lowered:
                response = await self.kernel.invoke("excursion_skill", "search_excursions", context)
                skill_invoked = True
            elif "restaurant" in lowered:
                response = await self.kernel.invoke("restaurant_skill", "search_restaurants", context)
                skill_invoked = True
            elif "hotel" in lowered:
                response = await self.kernel.invoke("hotel_skill", "search_hotels", context)
                skill_invoked = True
            elif "flight" in lowered:
                response = await self.kernel.invoke("flight_skill", "search_flights", context)
                skill_invoked = True

            if not skill_invoked:
                response = "Sorry, I couldn't identify your request. Please mention excursion, restaurant, hotel, or flight."

            # Save assistant response
            await self.save_conversation_state(conversation_id, response, "assistant")

            return {
                "success": True,
                "response": response,
                "suggestions": self._generate_suggestions(lowered)
            }

        except Exception as e:
            self.logger.error(f"Error processing user input: {str(e)}")
            return {"success": False, "response": "An error occurred while processing your request."}

    def _generate_suggestions(self, message: str) -> List[str]:
        """Generate contextual suggestions based on the user's message."""
        suggestions = []
        if "flight" in message:
            suggestions = ["Check flight prices", "View flight details", "Compare airlines"]
        elif "hotel" in message:
            suggestions = ["View hotel amenities", "Check availability", "Compare rates"]
        elif "restaurant" in message:
            suggestions = ["View menu", "Check reviews", "Make a reservation"]
        elif "excursion" in message:
            suggestions = ["View activities", "Check availability", "Compare options"]
        return suggestions

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation from session storage if not expired."""
        self._cleanup_expired_sessions()
        if conversation_id in session_conversations:
            conversation, last_active = session_conversations[conversation_id]
            if datetime.now(timezone.utc) - last_active <= SESSION_TIMEOUT:
                # Update last activity time
                session_conversations[conversation_id] = (conversation, datetime.now(timezone.utc))
                return conversation
        return None

    def cleanup_session(self, conversation_id: str) -> None:
        """Clean up session data when conversation ends."""
        if conversation_id in session_conversations:
            del session_conversations[conversation_id]