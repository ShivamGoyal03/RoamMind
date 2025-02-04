from typing import List, Dict, Optional
import logging
from .models import Conversation, ConversationContext
from ..agents.base import BaseAgent, AgentRequest, AgentResponse
from ..agents.flight_agent import FlightAgent
from ..agents.hotel_agent import HotelAgent
from ..agents.excursion_agent import ExcursionAgent
from ..agents.restaurant_agent import RestaurantAgent
from ..infrastructure.azure_openai import AzureOpenAIService
from ..infrastructure.cosmos_repository import CosmosRepository

class Orchestrator:
    """Orchestrator for coordinating between different agents and managing conversations."""
    
    def __init__(
        self,
        flight_agent: FlightAgent,
        hotel_agent: HotelAgent,
        excursion_agent: ExcursionAgent,
        restaurant_agent: RestaurantAgent,
        openai_service: AzureOpenAIService,
        repository: CosmosRepository
    ):
        self.agents = {
            "flight": flight_agent,
            "hotel": hotel_agent,
            "excursion": excursion_agent,
            "restaurant": restaurant_agent
        }
        self.openai_service = openai_service
        self.repository = repository
        self.logger = logging.getLogger(__name__)
        
    async def process_user_input(self, conversation_id: str, message: str):
        """
        Process the user input by dispatching to the appropriate agent based on keywords in the message.
        Returns an AgentResponse.
        """
        lowered = message.lower()
        if "flight" in lowered:
            agent = self.agents.get("flight")
        elif "hotel" in lowered:
            agent = self.agents.get("hotel")
        elif "restaurant" in lowered:
            agent = self.agents.get("restaurant")
        elif "excursion" in lowered:
            agent = self.agents.get("excursion")
        else:
            # If no intent is identified, return a default response.
            return AgentResponse(
                success=True,
                response="Sorry, I couldn't identify your request. Please mention flight, hotel, restaurant, or excursion.",
                suggestions=[]
            )
        
        # Each agent is expected to have a process_message() method that returns an AgentResponse.
        return await agent.process_message(message)
            
    async def _coordinate_agents(
        self,
        user_input: str,
        analysis: Dict,
        context: ConversationContext
    ) -> AgentResponse:
        """Coordinate between multiple agents for complex requests."""
        try:
            responses = {}
            for agent_type, params in analysis["agent_params"].items():
                agent = self.agents.get(agent_type)
                if agent:
                    response = await agent.process(
                        AgentRequest(
                            input=user_input,
                            context=context,
                            parameters=params
                        )
                    )
                    responses[agent_type] = response
                    
            # Combine responses using LLM
            combined_response = await self.openai_service.combine_agent_responses(
                responses,
                analysis
            )
            
            return AgentResponse(
                success=True,
                response=combined_response["message"],
                data=combined_response["data"],
                updated_context={
                    agent_type: resp.updated_context
                    for agent_type, resp in responses.items()
                },
                suggestions=combined_response["suggestions"]
            )
            
        except Exception as e:
            self.logger.error(f"Coordination error: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                response="Sorry, I had trouble coordinating the travel planning.",
                suggestions=["Try simpler request", "Plan step by step"]
            )
            
    async def _get_primary_agent(self, intent: str) -> Optional[BaseAgent]:
        """Get the primary agent for handling a specific intent."""
        for agent in self.agents.values():
            if await agent.can_handle(intent):
                return agent
        return None

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by its ID."""
        try:
            conversation = await self.repository.get_conversation(conversation_id)
            return conversation
        except Exception as e:
            self.logger.error(f"Error retrieving conversation: {str(e)}", exc_info=True)
            return None