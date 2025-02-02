from typing import List, Optional
from .base import BaseAgent, AgentRequest, AgentResponse
from ..infrastructure.flight_service import FlightService
from ..infrastructure.azure_openai import AzureOpenAIService
from ..models.flight import FlightSearchParams, Flight
from ..exceptions import FlightNotFoundError
from ..utils.logger import setup_logger
from ..utils.date_helper import parse_date_string
from pydantic import ValidationError

logger = setup_logger(__name__)

class FlightAgent(BaseAgent):
    """Agent for handling flight-related queries."""

    SUPPORTED_INTENTS = {
        "search_flights",
        "flight_info",
        "check_availability",
        "flight_status"
    }

    def __init__(self, flight_service: FlightService, openai_service: AzureOpenAIService):
        logger.info("Initializing FlightAgent")
        self.flight_service = flight_service
        self.openai_service = openai_service

    async def can_handle(self, intent: str) -> bool:
        return intent.lower() in self.SUPPORTED_INTENTS

    async def get_name(self) -> str:
        return "Flight Agent"

    async def get_description(self) -> str:
        return "I can help you search for flights and check flight status."

    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            intent = request.get_parameter("intent", "").lower()
            logger.info(f"Processing flight intent: {intent}")

            if intent == "search_flights":
                return await self._handle_flight_search(request)
            elif intent == "flight_info":
                return await self._handle_flight_info(request)
            elif intent == "check_availability":
                return await self._handle_availability_check(request)
            elif intent == "flight_status":
                return await self._handle_flight_status(request)

            return AgentResponse(
                success=False,
                response="I'm not sure how to help with that. Would you like to search for flights?",
                suggestions=["Search flights", "Check flight status", "View popular routes"]
            )

        except ValidationError as e:
            logger.error(f"Validation error processing flight request: {e}. User Input: {request.input}")
            return AgentResponse(success=False, response=f"Invalid input: Please review your request and try again.", suggestions=["Try again", "Check your input"])
        except FlightNotFoundError as e:
            logger.error(f"Flight not found: {e}. User Input: {request.input}, Intent: {request.get_parameter('intent', 'N/A')}")
            return AgentResponse(success=False, response=f"I couldn't find any flights matching your criteria. Please try adjusting your search parameters.", suggestions=["Try again", "Refine your search"])
        except Exception as e:
            logger.exception(f"Unexpected error processing flight request: {e}. User Input: {request.input}")
            return AgentResponse(success=False, response="Sorry, an unexpected error occurred. Please try again later.", suggestions=[])

    async def _handle_flight_search(self, request: AgentRequest) -> AgentResponse:
        logger.info("Handling flight search request")
        try:
            search_info = await self.openai_service.extract_flight_information(request.input, request.context)
            search_params = FlightSearchParams(**search_info)
            flights = await self.flight_service.search_flights(search_params)

            if not flights:
                return AgentResponse(
                    success=True,
                    response="No flights found matching your criteria. Would you like to try different options?",
                    suggestions=[
                        "Try different dates",
                        "Check nearby airports",
                        "Adjust price range",
                        "Specify different airlines"
                    ]
                )

            return AgentResponse(
                success=True,
                response=self._format_flight_results(flights),
                data={"flights": [f.to_dict() for f in flights]},
                suggestions=[
                    "View more details",
                    "Compare flights",
                    "Refine search"
                ]
            )
        except ValidationError as e:
            logger.error(f"Invalid search parameters: {e}")
            return AgentResponse(success=False, response=f"Invalid search parameters: {e}", suggestions=["Try again", "Specify your search correctly"])
        except Exception as e:
            logger.exception(f"Error searching flights: {e}")
            return AgentResponse(success=False, response=f"Failed to search flights: {e}", suggestions=["Try again", "Check your input"])


    async def _handle_flight_status(self, request: AgentRequest) -> AgentResponse:
        try:
            flight_number = request.get_parameter("flight_number")
            if not flight_number:
                return AgentResponse(
                    success=False,
                    response="Please provide a flight number to check status.",
                    suggestions=["Search flights"]
                )

            flight = await self.flight_service.get_flight_details(flight_number)

            return AgentResponse(
                success=True,
                response=self._format_flight_details(flight),
                data={"flight": flight.to_dict()},
                suggestions=["Get updates", "View route map", "Check baggage policy"]
            )

        except FlightNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that flight. Please check the flight number.",
                suggestions=["Search flights"]
            )

    async def _handle_flight_info(self, request: AgentRequest) -> AgentResponse:
        """Handle requests for detailed flight information."""
        logger.info("Handling flight info request")
        flight_id = request.get_parameter("flight_id")

        if not flight_id:
            return AgentResponse(
                success=False,
                response="Please specify which flight you'd like to know more about.",
                suggestions=["Search flights", "Check flight status"]
            )

        try:
            flight = await self.flight_service.get_flight_details(flight_id)
            return AgentResponse(
                success=True,
                response=self._format_flight_details(flight),
                data={"flight": flight.to_dict()},
                suggestions=["View baggage rules", "Compare with other flights"]
            )
        except FlightNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that flight.",
                suggestions=["Search flights", "View popular routes"]
            )

    async def _handle_availability_check(self, request: AgentRequest) -> AgentResponse:
        """Handle flight availability check requests."""
        logger.info("Handling availability check request")
        flight_id = request.get_parameter("flight_id")
        date_str = request.get_parameter("date")
        seats = request.get_parameter("seats", 1)

        if not all([flight_id, date_str]):
            return AgentResponse(
                success=False,
                response="Please provide the flight and date to check availability.",
                suggestions=["Search flights first", "View flight schedule"]
            )

        try:
            date = parse_date_string(date_str)
            availability = await self.flight_service.check_availability(
                flight_id=flight_id,
                date=date,
                seats=seats
            )

            if availability.get("is_available"):
                flight = await self.flight_service.get_flight_details(flight_id)
                return AgentResponse(
                    success=True,
                    response=(
                        f"Good news! {flight.airline} flight {flight.flight_number} has "
                        f"{seats} seat(s) available on {date.strftime('%B %d')}.\n"
                        f"Price: ${availability.get('price', 0):.2f} per person\n"
                        f"{availability.get('notes', '')}"
                    ),
                    data={
                        "availability": availability,
                        "flight": flight.to_dict()
                    },
                    suggestions=["View more details", "Check other dates", "View flight details"]
                )
            else:
                return AgentResponse(
                    success=True,
                    response=(
                        f"Sorry, the flight is not available for {seats} passenger(s) "
                        f"on {date.strftime('%B %d')}.\n"
                        f"{availability.get('alternative_suggestions', '')}"
                    ),
                    data={"availability": availability},
                    suggestions=["Check other dates", "Search different flights"]
                )

        except FlightNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that flight.",
                suggestions=["Search flights", "View flight schedule"]
            )

    def _format_flight_results(self, flights: List[Flight]) -> str:
        """Format flight search results into readable text."""
        if not flights:
            return "No flights found."

        response = "Here are the available flights:\n\n"
        for i, flight in enumerate(flights, 1):
            response += (
                f"{i}. {flight.airline} Flight {flight.flight_number}\n"
                f"   {flight.departure_airport} → {flight.arrival_airport}\n"
                f"   Departure: {flight.departure_time.strftime('%B %d, %I:%M %p')}\n"
                f"   Arrival: {flight.arrival_time.strftime('%B %d, %I:%M %p')}\n"
                f"   Price: ${flight.price:.2f}\n\n"
            )

        return response

    def _format_flight_details(self, flight: Flight) -> str:
        """Format detailed flight information into readable text."""
        return (
            f"Flight Details:\n\n"
            f"{flight.airline} Flight {flight.flight_number}\n"
            f"Route: {flight.departure_airport} → {flight.arrival_airport}\n"
            f"Departure: {flight.departure_time.strftime('%I:%M %p, %B %d')}\n"
            f"Arrival: {flight.arrival_time.strftime('%I:%M %p, %B %d')}\n"
            f"Duration: {flight.duration} minutes\n"
            f"Aircraft: {flight.aircraft_type}\n"
            f"Class: {flight.cabin_class}\n"
            f"Price: ${flight.price:.2f}\n"
            f"Baggage allowance: {flight.baggage_allowance}\n"
            f"Additional info: {flight.additional_info or 'None'}"
        )