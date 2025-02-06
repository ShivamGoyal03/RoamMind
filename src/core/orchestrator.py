import logging
from typing import Dict, Optional, Any
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..core.config import get_settings
from ..infrastructure.cosmos_repository import CosmosRepository
from ..models import Conversation

from ..infrastructure import (
    AzureOpenAIService,
    CosmosRepository
)

from ..skills import (
    ExcursionSkill,
    RestaurantSkill,
    HotelSkill,
    FlightSkill
)

class Orchestrator:
    """Orchestrator for coordinating between different agents and managing conversations.
       This orchestrator integrates the excursion, restaurant, hotel, and flight skill plugins.
    """

    def __init__(self, repository: CosmosRepository):
        self.logger = logging.getLogger(__name__)
        self.repository = repository
        
        # Obtain configuration settings
        settings = get_settings()
        
        # Properly initialize the Kernel using configuration settings
        self.kernel = Kernel(endpoint=settings.azure_openai_endpoint, api_key=settings.azure_openai_api_key)
        
        # Now initialize the AzureOpenAIService using the kernel
        self.azure_service = AzureOpenAIService(self.kernel)
        
        # Initialize and add the skill plugins to the kernel.
        self.excursion_skill = ExcursionSkill(self.kernel)
        self.restaurant_skill = RestaurantSkill(self.kernel)
        self.hotel_skill = HotelSkill(self.kernel)
        self.flight_skill = FlightSkill(self.kernel)

    async def process_user_input(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """
        Process user input and return a dictionary response.
        This function uses keyword matching to determine which skill to invoke.
        The dictionary contains 'success', 'response', and 'suggestions' keys.
        """
        lowered = message.lower()
        response = ""
        skill_invoked = False
        context = KernelArguments({"input": message})

        # Determine which skill to invoke based on keyword matching.
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

        return {"success": True, "response": response, "suggestions": []}

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by its ID from the Cosmos repository."""
        try:
            conversation = await self.repository.get_conversation(conversation_id)
            return conversation
        except Exception as e:
            self.logger.error(f"Error retrieving conversation: {str(e)}", exc_info=True)
            return None