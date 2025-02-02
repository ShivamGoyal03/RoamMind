from typing import List
from .base import BaseAgent, AgentRequest, AgentResponse
from ..infrastructure.hotel_service import HotelService
from ..infrastructure.azure_openai import AzureOpenAIService
from ..models.hotel import HotelSearchParams, Hotel
from ..exceptions import HotelNotFoundError
from ..utils.date_helper import parse_date_string
from ..utils.logger import setup_logger, ValidationError

logger = setup_logger(__name__)

class HotelAgent(BaseAgent):
    """Agent for handling hotel-related queries."""

    SUPPORTED_INTENTS = {
        "search_hotels",
        "hotel_info",
        "check_availability"
    }

    def __init__(self, hotel_service: HotelService, openai_service: AzureOpenAIService):
        logger.info("Initializing HotelAgent")
        self.hotel_service = hotel_service
        self.openai_service = openai_service

    async def can_handle(self, intent: str) -> bool:
        return intent.lower() in self.SUPPORTED_INTENTS

    async def get_name(self) -> str:
        return "Hotel Agent"

    async def get_description(self) -> str:
        return "I can help you find hotels and check availability."

    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            intent = request.get_parameter("intent", "").lower()
            logger.info(f"Processing hotel intent: {intent}")

            if intent == "search_hotels":
                return await self._handle_hotel_search(request)
            elif intent == "hotel_info":
                return await self._handle_hotel_info(request)
            elif intent == "check_availability":
                return await self._handle_availability_check(request)

            return AgentResponse(
                success=False,
                response="I'm not sure how to help with that. Would you like to search for hotels?",
                suggestions=["Search hotels", "Check availability", "View popular hotels"]
            )

        except ValidationError as e:
            logger.error(f"Validation error processing hotel request: {e}. User Input: {request.input}")
            return AgentResponse(success=False, response=f"Invalid input: Please review your request and try again.", suggestions=["Try again", "Check your input"])
        except (HotelNotFoundError) as e: #More specific exception handling
            logger.error(f"Error during API interaction: {e}. User Input: {request.input}, Intent: {request.get_parameter('intent', 'N/A')}")
            return AgentResponse(success=False, response=f"There was a problem processing your request. Please try again later.", suggestions=["Try again"])
        except Exception as e:
            logger.exception(f"Unexpected error processing hotel request: {e}. User Input: {request.input}")
            return AgentResponse(success=False, response="Sorry, an unexpected error occurred. Please try again later.", suggestions=[])


    async def _handle_hotel_search(self, request: AgentRequest) -> AgentResponse:
        search_info = await self.openai_service.extract_hotel_information(request.input, request.context)

        try:
            search_params = HotelSearchParams(**search_info)
            hotels = await self.hotel_service.search_hotels(search_params)
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Failed to search hotels: {str(e)}",
                suggestions=["Try different dates", "Modify search criteria"]
            )

        if not hotels:
            return AgentResponse(
                success=True,
                response="I couldn't find any hotels matching your criteria. Would you like to try different options?",
                suggestions=[
                    "Try different dates",
                    "Increase price range",
                    "Change location",
                    "Refine your search"
                ]
            )

        return AgentResponse(
            success=True,
            response=self._format_hotel_results(hotels),
            data={"hotels": [h.to_dict() for h in hotels]},
            suggestions=[
                "Show more details",
                "Check availability",
                "View other hotels" #Removed "Book a room"
            ]
        )

    async def _handle_hotel_info(self, request: AgentRequest) -> AgentResponse:
        hotel_id = request.get_parameter("hotel_id")

        if not hotel_id:
            return AgentResponse(
                success=False,
                response="Please specify which hotel you'd like to know more about.",
                suggestions=["Search hotels", "View popular hotels"]
            )

        try:
            hotel = await self.hotel_service.get_hotel_details(hotel_id)
            return AgentResponse(
                success=True,
                response=self._format_hotel_details(hotel),
                data={"hotel": hotel.to_dict()},
                suggestions=["Check availability", "View rooms", "View similar hotels"] 
            )
        except HotelNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that hotel.",
                suggestions=["Search hotels", "View popular hotels"]
            )

    async def _handle_availability_check(self, request: AgentRequest) -> AgentResponse:
        hotel_id = request.get_parameter("hotel_id")
        room_id = request.get_parameter("room_id")
        check_in_str = request.get_parameter("check_in")
        check_out_str = request.get_parameter("check_out")
        guests = request.get_parameter("guests", 1)

        if not all([hotel_id, room_id, check_in_str, check_out_str]):
            return AgentResponse(
                success=False,
                response="Please provide hotel, room, and dates to check availability.",
                suggestions=["Search hotels first", "View popular hotels"]
            )

        try:
            check_in = parse_date_string(check_in_str)
            check_out = parse_date_string(check_out_str)

            availability = await self.hotel_service.check_availability(
                hotel_id=hotel_id,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
                guests=guests
            )

            if availability.get("is_available"):
                hotel = await self.hotel_service.get_hotel_details(hotel_id)
                room = next((r for r in hotel.rooms if r.id == room_id), None)

                return AgentResponse(
                    success=True,
                    response=(
                        f"The {room.type if room else 'room'} is available for your dates.\n"
                        f"Price: ${availability.get('total_price', 0):.2f} total for {(check_out - check_in).days} nights.\n"
                        f"{availability.get('message', '')}"
                    ),
                    data={
                        "availability": availability,
                        "hotel": hotel.to_dict() if hotel else None
                    },
                    suggestions=[
                        "View room details",
                        "Check other dates",
                        "View similar hotels" 
                    ]
                )
            else:
                return AgentResponse(
                    success=True,
                    response=(
                        f"Sorry, the room is not available for your dates.\n"
                        f"{availability.get('alternative_suggestions', '')}"
                    ),
                    data={"availability": availability},
                    suggestions=[
                        "Check other dates",
                        "View other rooms",
                        "Search different hotels"
                    ]
                )

        except HotelNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that hotel.",
                suggestions=["Search hotels", "View popular hotels"]
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Error checking availability: {str(e)}",
                suggestions=["Try again", "Search different hotels"]
            )
        
    def _format_hotel_results(self, hotels: List[Hotel]) -> str:
        """Format hotel search results into a readable message."""
        if not hotels:
            return "No hotels found."
            
        response = "Here are the available hotels:\n\n"
        for i, hotel in enumerate(hotels, 1):
            lowest_price = min(room.price_per_night for room in hotel.rooms)
            response += (
                f"{i}. {hotel.name} {'⭐' * int(hotel.star_rating)}\n"
                f"   Location: {hotel.location}\n"
                f"   From ${lowest_price:.2f} per night\n"
                f"   Rating: {hotel.rating}/5 ({hotel.review_count} reviews)\n"
                f"   Amenities: {', '.join(hotel.amenities[:3])}...\n\n"
            )
        
        return response
        
    def _format_hotel_details(self, hotel: Hotel) -> str:
        """Format detailed hotel information."""
        return (
            f"🏨 {hotel.name} {'⭐' * int(hotel.star_rating)}\n\n"
            f"📍 {hotel.address}\n"
            f"Rating: {hotel.rating}/5 ({hotel.review_count} reviews)\n\n"
            f"Description:\n{hotel.description}\n\n"
            f"Amenities:\n" + "\n".join(f"• {amenity}" for amenity in hotel.amenities) + "\n\n"
            f"Available Rooms:\n" + "\n".join(
                f"• {room.type}: ${room.price_per_night:.2f}/night ({room.bed_type} bed, {room.capacity} guests max)"
                for room in hotel.rooms
            ) + "\n\n"
            f"Check-in: {hotel.check_in_time}\n"
            f"Check-out: {hotel.check_out_time}"
        )