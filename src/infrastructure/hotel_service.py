from typing import List, Dict, Optional
from datetime import datetime, timedelta
import aiohttp
import asyncio
from ..models.hotel import Hotel, HotelSearchParams, Room
from ..exceptions import HotelNotFoundError
from ..infrastructure.azure_openai import AzureOpenAIService
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class HotelService:
    """Service for handling hotel-related operations through external APIs and LLM."""

    def __init__(
        self,
        api_key: str,
        api_base_url: str,
        openai_service: AzureOpenAIService,
        client_session: Optional[aiohttp.ClientSession] = None
    ):
        logger.info("Initializing HotelService")
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.openai_service = openai_service
        self.client_session = client_session or aiohttp.ClientSession()

    async def close(self):
        await self.client_session.close()

    async def search_hotels(self, params: HotelSearchParams) -> List[Hotel]:
        try:
            logger.info(f"Searching hotels with params: {params.model_dump()}")
            api_response = await self._call_api("GET", "/hotels/search", params=params.model_dump())
            if not api_response.get("hotels"):
                return []
            enhanced_results = await self.openai_service.enhance_hotel_results(api_response["hotels"], params.model_dump())
            return [Hotel(**hotel) for hotel in enhanced_results]
        except Exception as e:
            logger.exception(f"Error searching hotels: {e}")
            raise

    async def get_hotel_details(self, hotel_id: str) -> Hotel:
        try:
            logger.info(f"Fetching details for hotel: {hotel_id}")
            api_response = await self._call_api("GET", f"/hotels/{hotel_id}")
            if not api_response:
                raise HotelNotFoundError(f"Hotel {hotel_id} not found")
            enhanced_details = await self.openai_service.enhance_hotel_details(api_response)
            return Hotel(**enhanced_details)
        except Exception as e:
            logger.exception(f"Error fetching hotel details: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error fetching hotel details: {e}")
            raise


    async def check_availability(
        self,
        hotel_id: str,
        room_id: str,
        check_in: datetime,
        check_out: datetime,
        guests: int
    ) -> Dict:
        try:
            logger.info(f"Checking availability for hotel {hotel_id}, room {room_id}, check-in: {check_in}, check-out: {check_out}, guests: {guests}")
            availability = await self._call_api(
                "GET",
                f"/hotels/{hotel_id}/rooms/{room_id}/availability",
                params={
                    "check_in": check_in.isoformat(),
                    "check_out": check_out.isoformat(),
                    "guests": guests
                }
            )

            enhanced_response = await self.openai_service.enhance_hotel_availability(
                availability,
                hotel_id,
                room_id,
                check_in,
                check_out,
                guests
            )

            return enhanced_response

        except Exception as e:
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
                    raise Exception(f"API connection failed after {max_retries} retries: {e}") from e
                logger.warning(f"API call failed (attempt {attempt}/{max_retries}): {e}. Retrying...")
                await asyncio.sleep(2**attempt)
            except aiohttp.ClientResponseError as e:
                logger.error(f"API request failed with status code {e.status}: {e}")
                raise Exception(f"API request failed with status code {e.status}: {e}") from e