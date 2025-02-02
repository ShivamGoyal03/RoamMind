from typing import List, Dict, Optional
import aiohttp
from ..models.restaurant import Restaurant, RestaurantSearchParams
from ..exceptions import RestaurantNotFoundError
from ..infrastructure.azure_openai import AzureOpenAIService
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class RestaurantService:
    """Service for handling restaurant-related operations through external APIs."""

    def __init__(self, api_key: str, api_base_url: str, openai_service: AzureOpenAIService):
        logger.info("Initializing RestaurantService")
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.openai_service = openai_service

    async def search_restaurants(self, params: RestaurantSearchParams) -> List[Restaurant]:
        """Search for restaurants using external API."""
        try:
            logger.info(f"Searching restaurants with params: {params.dict()}")
            api_response = await self._call_api("GET", "/restaurants/search", params=params.dict())
            if not api_response.get("restaurants"):
                logger.info("No restaurants found")
                return []
            return [Restaurant(**r) for r in api_response["restaurants"]]
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            raise

    async def get_restaurant_details(self, restaurant_id: str) -> Restaurant:
        """Get restaurant details from API."""
        try:
            api_response = await self._call_api("GET", f"/restaurants/{restaurant_id}")
            if not api_response:
                raise RestaurantNotFoundError(f"Restaurant {restaurant_id} not found")
            return Restaurant(**api_response)
        except Exception as e:
            raise RestaurantNotFoundError(f"Error fetching restaurant details: {str(e)}")

    async def get_menu(self, restaurant_id: str) -> Dict:
        """Get menu with LLM-enhanced descriptions and recommendations."""
        try:
            menu_data = await self._call_api(
                "GET",
                f"/restaurants/{restaurant_id}/menu"
            )
            
            enhanced_menu = await self.openai_service.enhance_menu_details(
                menu_data,
                restaurant_id
            )
            
            return enhanced_menu
            
        except Exception as e:
            raise Exception(f"Error fetching menu: {str(e)}")
            
    async def get_reviews(self, restaurant_id: str, limit: int = 10) -> Dict:
        """Get reviews with LLM analysis and summary."""
        try:
            reviews = await self._call_api(
                "GET",
                f"/restaurants/{restaurant_id}/reviews",
                params={"limit": limit}
            )
            
            enhanced_reviews = await self.openai_service.analyze_restaurant_reviews(
                reviews,
                restaurant_id
            )
            
            return enhanced_reviews
            
        except Exception as e:
            raise Exception(f"Error fetching reviews: {str(e)}")
            
    async def get_recommendations(
        self,
        cuisine: Optional[str] = None,
        location: Optional[str] = None,
        preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """Get personalized restaurant recommendations using LLM."""
        try:
            base_recommendations = await self._call_api(
                "GET",
                "/restaurants/recommendations",
                params={
                    "cuisine": cuisine,
                    "location": location
                }
            )
            
            enhanced_recommendations = await self.openai_service.enhance_restaurant_recommendations(
                base_recommendations,
                preferences
            )
            
            return enhanced_recommendations
            
        except Exception as e:
            raise Exception(f"Error getting recommendations: {str(e)}")
            
    async def _call_api(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make API calls with proper error handling."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                async with session.request(method, f"{self.api_base_url}{endpoint}", headers=headers, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"API call failed: {str(e)}")
