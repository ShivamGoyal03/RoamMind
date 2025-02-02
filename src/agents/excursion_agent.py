from typing import List
from datetime import datetime
from .base import BaseAgent, AgentRequest, AgentResponse
from ..infrastructure.excursion_service import ExcursionService
from ..infrastructure.azure_openai import AzureOpenAIService
from ..models.excursion import ExcursionSearchParams, Excursion
from ..exceptions import BookingError, ExcursionNotFoundError
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ExcursionAgent(BaseAgent):
    """Agent for handling excursion-related queries."""
    
    SUPPORTED_INTENTS = {
        "search_excursions",
        "book_excursion",
        "excursion_info",
        "cancel_excursion",
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
        return "I can help you find and book excursions, tours, and activities at your destination."
        
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            intent = request.get_parameter("intent", "").lower()
            logger.info(f"Processing excursion intent: {intent}")
            
            if intent == "search_excursions":
                return await self._handle_excursion_search(request)
            elif intent == "book_excursion":
                return await self._handle_excursion_booking(request)
            elif intent == "excursion_info":
                return await self._handle_excursion_info(request)
            elif intent == "cancel_excursion":
                return await self._handle_excursion_cancellation(request)
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
                "Book an excursion",
                "Filter by category"
            ]
        )
            
    async def _handle_excursion_booking(self, request: AgentRequest) -> AgentResponse:
        excursion_id = request.get_parameter("excursion_id")
        date_str = request.get_parameter("date")
        participants = request.get_parameter("participants", 1)
        customer_details = request.get_parameter("customer_details", {})
        
        if not all([excursion_id, date_str, customer_details]):
            return AgentResponse(
                success=False,
                response="Please provide excursion details, date, and customer information to make a booking.",
                suggestions=["Search excursions first", "View available dates"]
            )
        
        try:
            date = datetime.fromisoformat(date_str)
            booking = await self.excursion_service.create_booking(
                excursion_id=excursion_id,
                date=date,
                participants=participants,
                customer_details=customer_details
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Booking failed: {str(e)}",
                suggestions=["Try again", "Choose different date"]
            )
            
        return AgentResponse(
            success=True,
            response=f"Great! I've booked your excursion. Your booking reference is {booking.reference}.",
            data={"booking": booking.to_dict()},
            suggestions=[
                "View booking details",
                "Search more activities",
                "Cancel booking"
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
            suggestions=["Book now", "Check availability", "View similar activities"]
        )
            
    async def _handle_excursion_cancellation(self, request: AgentRequest) -> AgentResponse:
        booking_ref = request.get_parameter("booking_reference")
        customer_email = request.get_parameter("customer_email")
        
        if not all([booking_ref, customer_email]):
            return AgentResponse(
                success=False,
                response="Please provide your booking reference and email to cancel.",
                suggestions=["View my bookings", "Search excursions"]
            )
            
        try:
            result = await self.excursion_service.cancel_booking(booking_ref, customer_email)
        except BookingError as e:
            return AgentResponse(
                success=False,
                response=f"Failed to cancel booking: {str(e)}",
                suggestions=["Try again later", "Contact support"]
            )
            
        return AgentResponse(
            success=True,
            response=f"Your booking has been cancelled. {result['message']}",
            data=result,
            suggestions=["Search new activities", "View other excursions"]
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
            f"Languages: {', '.join(excursion.languages)}\n"
            f"Maximum Group Size: {excursion.max_participants} people"
        )