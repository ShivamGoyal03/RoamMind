from typing import List, Dict
import aiohttp
from ..models.excursion import Excursion, ExcursionSearchParams
from ..exceptions import ExcursionNotFoundError
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
                raise ExcursionNotFoundError(excursion_id)

            # Use LLM to enhance description and details
            enhanced_details = await self.openai_service.enhance_excursion_details(
                api_response
            )

            return Excursion(**enhanced_details)

        except Exception as e:
            logger.error(f"Error fetching excursion details: {str(e)}")
            raise ExcursionNotFoundError(f"Error fetching excursion details: {str(e)}")

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