from typing import List
from .base import BaseAgent, AgentRequest, AgentResponse
from ..infrastructure.excursion_service import ExcursionService
from ..infrastructure.azure_openai import AzureOpenAIService
from ..models.excursion import ExcursionSearchParams, Excursion
from ..exceptions import ExcursionNotFoundError
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ExcursionAgent(BaseAgent):
    """Agent for handling excursion-related queries."""
    
    SUPPORTED_INTENTS = {
        "search_excursions",
        "excursion_info",
        "list_categories"
    }
    
    def __init__(self, excursion_service: ExcursionService, openai_service: AzureOpenAIService):
        logger.info("Initializing ExcursionAgent")
        self.excursion_service = excursion_service
        self.openai_service = openai_service
        
    async def can_handle(self, intent: str) -> bool:
        return intent.lower() in self.SUPPORTED_INTENTS
        
    async def get_name(self) -> str:
        return "Excursion Agent"
        
    async def get_description(self) -> str:
        return "I can provide information about excursions, tours, and activities at your destination."
        
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            intent = request.get_parameter("intent", "").lower()
            logger.info(f"Processing excursion intent: {intent}")
            
            if intent == "search_excursions":
                return await self._handle_excursion_search(request)
            elif intent == "excursion_info":
                return await self._handle_excursion_info(request)
            elif intent == "list_categories":
                return await self._handle_list_categories(request)
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Sorry, I encountered an error: {str(e)}",
                suggestions=["Try again", "Search different activities"]
            )
            
        return AgentResponse(
            success=False,
            response="I'm not sure how to handle that request. Would you like to search for excursions?",
            suggestions=["Search excursions", "View categories", "Popular activities"]
        )
            
    async def _handle_excursion_search(self, request: AgentRequest) -> AgentResponse:
        search_info = await self.openai_service.extract_excursion_information(
            request.input,
            request.context
        )
        
        try:
            search_params = ExcursionSearchParams(**search_info)
            excursions = await self.excursion_service.search_excursions(search_params)
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Failed to search excursions: {str(e)}",
                suggestions=["Try again", "Modify search criteria"]
            )
            
        if not excursions:
            return AgentResponse(
                success=True,
                response="I couldn't find any excursions matching your criteria. Would you like to try different options?",
                suggestions=[
                    "Try different dates",
                    "View all categories",
                    "Change location"
                ]
            )
            
        return AgentResponse(
            success=True,
            response=self._format_excursion_results(excursions),
            updated_context={
                "last_searched_excursions": [e.model_dump() for e in excursions],
                "search_params": search_params.model_dump()
            },
            data={"excursions": [e.model_dump() for e in excursions]},
            suggestions=[
                "Show more details",
                "Filter by category",
                "View similar activities"
            ]
        )
            
    async def _handle_excursion_info(self, request: AgentRequest) -> AgentResponse:
        excursion_id = request.get_parameter("excursion_id")
        if not excursion_id:
            return AgentResponse(
                success=False,
                response="Please specify which excursion you'd like to know more about.",
                suggestions=["Search excursions", "View popular activities"]
            )
            
        try:
            excursion = await self.excursion_service.get_excursion_details(excursion_id)
        except ExcursionNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that excursion.",
                suggestions=["Search excursions", "View popular activities"]
            )
            
        return AgentResponse(
            success=True,
            response=self._format_excursion_details(excursion),
            data={"excursion": excursion.to_dict()},
            suggestions=["View similar activities"]
        )
                
    async def _handle_list_categories(self, request: AgentRequest) -> AgentResponse:
        location = request.get_parameter("location", "")
        
        try:
            categories = await self.excursion_service.list_categories(location)
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Failed to fetch categories: {str(e)}",
                suggestions=["Try again", "Search excursions"]
            )
            
        return AgentResponse(
            success=True,
            response="Here are the available activity categories:\n\n" + 
                    "\n".join(f"• {category}" for category in categories),
            data={"categories": categories},
            suggestions=[f"Show {cat} activities" for cat in categories[:3]]
        )
            
    def _format_excursion_results(self, excursions: List[Excursion]) -> str:
        if not excursions:
            return "No excursions found."
            
        response = "Here are the available excursions:\n\n"
        for i, excursion in enumerate(excursions, 1):
            response += (
                f"{i}. {excursion.name}\n"
                f"   {excursion.category} | {excursion.duration} hours\n"
                f"   Price: ${excursion.price:.2f} per person\n"
                f"   {excursion.description[:100]}...\n\n"
            )
        
        return response
        
    def _format_excursion_details(self, excursion: Excursion) -> str:
        return (
            f"📍 {excursion.name}\n\n"
            f"Category: {excursion.category}\n"
            f"Duration: {excursion.duration} hours\n"
            f"Price: ${excursion.price:.2f} per person\n\n"
            f"Description:\n{excursion.description}\n\n"
            f"Includes:\n" + "\n".join(f"• {item}" for item in excursion.inclusions) + "\n\n"
            f"Meeting Point: {excursion.meeting_point}\n"
            f"Languages: {', '.join(excursion.languages)}"
        )