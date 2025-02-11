import json
import logging
import aiohttp
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..infrastructure.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class HotelSkill:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        # Initialize the Azure service using the kernel.
        self.azure_service = AzureOpenAIService(kernel)
        
        # Register skill functions with the kernel.
        self.kernel.add_function(self.search_hotels)
        self.kernel.add_function(self.get_hotel_details)
        self.kernel.add_function(self.suggest_hotels)

    @kernel_function(
        description="Search for hotels based on location, star rating, and dates using external APIs.",
        name="search_hotels"
    )
    async def search_hotels(self, context: KernelArguments) -> str:
        try:
            location = context.get("location", "")
            stars = context.get("stars", "")
            check_in = context.get("check_in", "")
            check_out = context.get("check_out", "")
            
            if not location or not stars:
                context["error"] = "Location and star rating must be provided."
                return "Please provide both a location and star rating to search for hotels."

            # Attempt to call an external hotel search API.
            api_response = await self._fetch_hotel_data(location, stars, check_in, check_out)
            if api_response and "response" in api_response:
                response = api_response["response"]
            else:
                response = f"Found hotels in {location} with a {stars}-star rating for the dates {check_in} to {check_out}."
                
            context["success"] = "true"
            context["response"] = response
            return response

        except Exception as e:
            logger.error(f"Failed to search hotels: {str(e)}")
            context["error"] = f"Failed to search hotels: {str(e)}"
            return "Sorry, an error occurred while searching for hotels."

    @kernel_function(
        description="Get detailed information about a specific hotel from external APIs.",
        name="get_hotel_details"
    )
    async def get_hotel_details(self, context: KernelArguments) -> str:
        try:
            hotel_id = context.get("hotel_id", "")
            if not hotel_id:
                context["error"] = "Hotel ID must be provided."
                return "Please provide a hotel ID."

            # Call an external API to get hotel details.
            details = await self._fetch_hotel_details(hotel_id)
            if details and "details" in details:
                response = details["details"]
            else:
                response = f"Retrieved details for hotel {hotel_id}."
                
            context["success"] = "true"
            context["response"] = response
            return response

        except Exception as e:
            logger.error(f"Failed to get hotel details: {str(e)}")
            context["error"] = f"Failed to get hotel details: {str(e)}"
            return "Sorry, an error occurred while retrieving hotel details."

    @kernel_function(
        description="Suggest hotels based on user preferences using external APIs and LLM fallback.",
        name="suggest_hotels"
    )
    async def suggest_hotels(self, context: KernelArguments) -> str:
        try:
            budget = context.get("budget", "")
            amenities = context.get("amenities", "")
            
            # Attempt to get suggestions via external API.
            api_suggestions = await self._fetch_suggestions_api(budget, amenities)
            
            # If no suggestions are returned via the API, fall back to the LLM.
            if not api_suggestions:
                llm_suggestions = await self._generate_suggestions_via_llm(budget, amenities)
                suggestions = llm_suggestions
            else:
                suggestions = api_suggestions
            
            response = f"Based on your budget ({budget}) and preferred amenities ({amenities}), here are some hotel suggestions."
            context["success"] = "true"
            context["response"] = response
            context["suggestions"] = suggestions
            return response

        except Exception as e:
            logger.error(f"Failed to suggest hotels: {str(e)}")
            context["error"] = f"Failed to suggest hotels: {str(e)}"
            return "Sorry, an error occurred while generating hotel suggestions."

    async def _fetch_hotel_data(self, location: str, stars: str, check_in: str, check_out: str) -> dict:
        """
        Fetch hotel search results from an external API.
        """
        api_url = "https://api.example.com/hotel/search"  # Replace with your real API endpoint
        params = {
            "location": location,
            "stars": stars,
            "check_in": check_in,
            "check_out": check_out
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"Hotel API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling hotel API: {e}")
        return {}

    async def _fetch_hotel_details(self, hotel_id: str) -> dict:
        """
        Fetch detailed hotel information from an external API.
        """
        api_url = f"https://api.example.com/hotel/{hotel_id}/details"  # Replace with your real API endpoint
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"Hotel details API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling hotel details API: {e}")
        return {}

    async def _fetch_suggestions_api(self, budget: str, amenities: str) -> list:
        """
        Fetch hotel suggestions from an external API based on budget and amenities.
        """
        api_url = "https://api.example.com/hotel/suggestions"  # Replace with your real API endpoint
        params = {"budget": budget, "amenities": amenities}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("suggestions", [])
                    else:
                        logger.error(f"Suggestions API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling suggestions API: {e}")
        return []

    async def _generate_suggestions_via_llm(self, budget: str, amenities: str) -> list:
        """
        Use Semantic Kernel's LLM (via AzureOpenAIService) to generate hotel suggestions.
        """
        prompt = (
            f"Generate a JSON object with a 'suggestions' key containing hotel names that "
            f"match a budget of {budget} and offer amenities such as {amenities}."
        )
        try:
            result = await self.kernel.invoke(prompt)
            data = json.loads(result)
            return data.get("suggestions", [])
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
        return []