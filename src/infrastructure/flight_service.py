from typing import List, Dict, Optional
import aiohttp
from ..models.flight import Flight, FlightSearchParams
from ..exceptions import FlightNotFoundError, APIError, APIConnectionError
from ..infrastructure.azure_openai import AzureOpenAIService
import logging
import asyncio

logger = logging.getLogger(__name__)

class APIError(Exception):
    pass

class APIConnectionError(Exception):
    pass

class FlightService:
    """Service for handling flight-related operations through external APIs and LLM."""

    def __init__(
        self,
        api_key: str,
        api_base_url: str,
        openai_service: AzureOpenAIService,
        client_session: Optional[aiohttp.ClientSession] = None
    ):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.openai_service = openai_service
        self.client_session = client_session or aiohttp.ClientSession()

    async def close(self):
        await self.client_session.close()

    async def search_flights(self, params: FlightSearchParams) -> List[Flight]:
        try:
            logger.info(f"Searching flights with params: {params.dict()}")
            api_response = await self._call_api("GET", "/flights/search", params=params.dict())
            if not api_response.get("flights"):
                return []
            enhanced_results = await self.openai_service.enhance_flight_results(api_response["flights"], params.dict())
            return [Flight(**flight) for flight in enhanced_results]
        except (APIError, APIConnectionError) as e:
            logger.exception(f"Error searching flights: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error searching flights: {e}")
            raise

    async def get_flight_details(self, flight_id: str) -> Flight:
        try:
            logger.info(f"Fetching details for flight: {flight_id}")
            api_response = await self._call_api("GET", f"/flights/{flight_id}")
            if not api_response:
                raise FlightNotFoundError(f"Flight {flight_id} not found")
            enhanced_details = await self.openai_service.enhance_flight_details(api_response)
            return Flight(**enhanced_details)
        except (APIError, APIConnectionError) as e:
            logger.exception(f"Error fetching flight details: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error fetching flight details: {e}")
            raise


    async def check_availability(
        self,
        flight_id: str,
        seats: int,
        seat_class: Optional[str] = None
    ) -> Dict:
        try:
            logger.info(f"Checking availability for flight {flight_id}, seats: {seats}, class: {seat_class}")
            availability = await self._call_api(
                "GET",
                f"/flights/{flight_id}/availability",
                params={"seats": seats, "class": seat_class}
            )

            enhanced_response = await self.openai_service.enhance_flight_availability(
                availability,
                flight_id,
                seats,
                seat_class
            )

            return enhanced_response

        except (APIError, APIConnectionError) as e:
            logger.exception(f"Error checking availability: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error checking availability: {e}")
            raise


    async def _call_api(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.api_base_url}{endpoint}"
        logger.info(f"Making API call: {method} {url} with params: {kwargs.get('params', {})} ")
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                async with self.client_session.request(method, url, headers=headers, **kwargs) as response:
                    response.raise_for_status()
                    data = await response.json()
                    logger.info(f"API call successful. Response: {data}")
                    return data
            except aiohttp.ClientError as e:
                if attempt == max_retries:
                    logger.exception(f"API connection failed after {max_retries} retries: {e}")
                    raise APIConnectionError(f"API connection failed after {max_retries} retries: {e}") from e
                logger.warning(f"API call failed (attempt {attempt}/{max_retries}): {e}. Retrying...")
                await asyncio.sleep(2**attempt)
            except aiohttp.ClientResponseError as e:
                logger.error(f"API request failed with status code {e.status}: {e}")
                raise APIError(f"API request failed with status code {e.status}: {e}") from e