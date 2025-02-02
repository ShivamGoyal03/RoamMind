from typing import List, Dict, Optional
from datetime import datetime
import aiohttp
from ..models.excursion import Excursion, ExcursionSearchParams, ExcursionBooking
from ..exceptions import BookingError, ExcursionNotFoundError
from ..infrastructure.azure_openai import AzureOpenAIService
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ExcursionService:
    """Service for handling excursion-related operations through external APIs and LLM."""
    
    def __init__(
        self,
        api_key: str,
        api_base_url: str,
        openai_service: AzureOpenAIService
    ):
        logger.info("Initializing ExcursionService")
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.openai_service = openai_service
        
    async def search_excursions(self, params: ExcursionSearchParams) -> List[Excursion]:
        """Search for excursions using external API with LLM enhancements."""
        try:
            logger.info(f"Searching excursions with params: {params.model_dump()}")
            # Get raw results from API
            api_response = await self._call_api(
                "GET",
                "/excursions/search",
                params=params.model_dump()
            )
            
            if not api_response.get("excursions"):
                return []
                
            # Enhance results with LLM
            enhanced_results = await self.openai_service.enhance_excursion_results(
                api_response["excursions"],
                params.model_dump()
            )
            
            return [Excursion(**excursion) for excursion in enhanced_results]
            
        except Exception as e:
            logger.error(f"Error searching excursions: {str(e)}")
            raise Exception(f"Error searching excursions: {str(e)}")
            
    async def get_excursion_details(self, excursion_id: str) -> Excursion:
        """Get excursion details from API with LLM enhancements."""
        try:
            logger.info(f"Fetching details for excursion: {excursion_id}")
            # Get basic details from API
            api_response = await self._call_api(
                "GET",
                f"/excursions/{excursion_id}"
            )
            
            if not api_response:
                raise ExcursionNotFoundError(f"Excursion {excursion_id} not found")
                
            # Use LLM to enhance description and details
            enhanced_details = await self.openai_service.enhance_excursion_details(
                api_response
            )
            
            return Excursion(**enhanced_details)
            
        except Exception as e:
            logger.error(f"Error fetching excursion details: {str(e)}")
            raise ExcursionNotFoundError(f"Error fetching excursion details: {str(e)}")
            
    async def create_booking(
        self,
        excursion_id: str,
        date: datetime,
        participants: int,
        customer_details: Dict[str, str]
    ) -> ExcursionBooking:
        """Create booking through API with LLM validation."""
        try:
            logger.info(f"Creating booking for excursion: {excursion_id}")
            # Validate booking parameters with LLM
            validation_result = await self.openai_service.validate_excursion_booking(
                excursion_id, date, participants, customer_details
            )
            
            if not validation_result["is_valid"]:
                raise BookingError(validation_result["reason"])
                
            # Create booking through API
            booking_response = await self._call_api(
                "POST",
                "/bookings",
                json={
                    "excursion_id": excursion_id,
                    "date": date.isoformat(),
                    "participants": participants,
                    "customer_details": customer_details
                }
            )
            
            return ExcursionBooking(**booking_response)
            
        except Exception as e:
            logger.error(f"Failed to create booking: {str(e)}")
            raise BookingError(f"Failed to create booking: {str(e)}")
            
    async def cancel_booking(self, booking_reference: str, customer_email: str) -> Dict:
        """Cancel booking through API."""
        try:
            logger.info(f"Cancelling booking: {booking_reference}")
            response = await self._call_api(
                "POST",
                "/bookings/cancel",
                json={
                    "booking_reference": booking_reference,
                    "customer_email": customer_email
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to cancel booking: {str(e)}")
            raise BookingError(f"Failed to cancel booking: {str(e)}")
            
    async def list_categories(self, location: str) -> List[str]:
        """Get available categories with LLM suggestions."""
        try:
            logger.info(f"Fetching categories for location: {location}")
            # Get base categories from API
            api_response = await self._call_api(
                "GET",
                "/categories",
                params={"location": location}
            )
            
            # Enhance categories with LLM suggestions
            enhanced_categories = await self.openai_service.enhance_excursion_categories(
                api_response.get("categories", []),
                location
            )
            
            return enhanced_categories
            
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise Exception(f"Error fetching categories: {str(e)}")
            
    async def check_availability(
        self,
        excursion_id: str,
        date: datetime,
        participants: int
    ) -> Dict:
        """Check availability through API with LLM validation."""
        try:
            logger.info(f"Checking availability for excursion: {excursion_id}")
            availability = await self._call_api(
                "GET",
                f"/excursions/{excursion_id}/availability",
                params={
                    "date": date.isoformat(),
                    "participants": participants
                }
            )
            
            # Enhance response with LLM suggestions
            enhanced_response = await self.openai_service.enhance_availability_response(
                availability,
                excursion_id,
                date,
                participants
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            raise Exception(f"Error checking availability: {str(e)}")
            
    async def _call_api(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make API calls with proper error handling."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.request(
                    method,
                    f"{self.api_base_url}{endpoint}",
                    headers=headers,
                    **kwargs
                ) as response:
                    if response.status >= 400:
                        error_data = await response.json()
                        raise Exception(error_data.get("message", "API error"))
                        
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            logger.error(f"API call failed: {str(e)}")
            raise Exception(f"API call failed: {str(e)}") 