import json
import logging
import aiohttp
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..infrastructure.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class RestaurantSkill:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        # Initialize the Azure service using the kernel.
        self.azure_service = AzureOpenAIService(kernel)
        
        # Register skill functions with the kernel.
        self.kernel.add_function(self.search_restaurants)
        self.kernel.add_function(self.get_restaurant_details)
        self.kernel.add_function(self.suggest_restaurants)

    @kernel_function(
        description="Search for restaurants based on location and dining preferences using external APIs.",
        name="search_restaurants"
    )
    async def search_restaurants(self, context: KernelArguments) -> str:
        try:
            location = context.get("location", "")
            cuisine = context.get("cuisine", "")
            date = context.get("date", "")
            
            if not location or not cuisine:
                context["error"] = "Location and cuisine must be provided."
                return "Please provide both location and cuisine to search."

            # Attempt to call an external restaurant search API.
            api_response = await self._fetch_restaurant_data(location, cuisine, date)
            if api_response and "response" in api_response:
                response = api_response["response"]
            else:
                response = f"Found restaurants in {location} serving {cuisine} cuisine on {date}."
                
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to search restaurants: {str(e)}")
            context["error"] = f"Failed to search restaurants: {str(e)}"
            return "Sorry, an error occurred while searching for restaurants."

    @kernel_function(
        description="Get detailed information about a specific restaurant from external APIs.",
        name="get_restaurant_details"
    )
    async def get_restaurant_details(self, context: KernelArguments) -> str:
        try:
            restaurant_id = context.get("restaurant_id", "")
            if not restaurant_id:
                context["error"] = "Restaurant ID must be provided."
                return "Please provide a restaurant ID."

            # Call an external API to get restaurant details.
            details = await self._fetch_restaurant_details(restaurant_id)
            if details and "details" in details:
                response = details["details"]
            else:
                response = f"Retrieved details for restaurant {restaurant_id}."
                
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to get restaurant details: {str(e)}")
            context["error"] = f"Failed to get restaurant details: {str(e)}"
            return "Sorry, an error occurred while retrieving restaurant details."

    @kernel_function(
        description="Suggest restaurants based on user dining preferences using external APIs and LLM fallback.",
        name="suggest_restaurants"
    )
    async def suggest_restaurants(self, context: KernelArguments) -> str:
        try:
            budget = context.get("budget", "")
            cuisine = context.get("cuisine", "")
            
            # Attempt to get suggestions via external API.
            api_suggestions = await self._fetch_suggestions_api(budget, cuisine)
            
            # If no suggestions are returned via the API, fall back to the LLM.
            if not api_suggestions:
                llm_suggestions = await self._generate_suggestions_via_llm(budget, cuisine)
                suggestions = llm_suggestions
            else:
                suggestions = api_suggestions
            
            response = f"Based on your budget ({budget}) and preferred cuisine ({cuisine}), here are some restaurant suggestions."
            context["success"] = "true"
            context["response"] = response
            context["suggestions"] = suggestions
            return response
            
        except Exception as e:
            logger.error(f"Failed to suggest restaurants: {str(e)}")
            context["error"] = f"Failed to suggest restaurants: {str(e)}"
            return "Sorry, an error occurred while generating restaurant suggestions."

    async def _fetch_restaurant_data(self, location: str, cuisine: str, date: str) -> dict:
        """
        Fetch restaurant search results from an external API.
        """
        api_url = "https://api.example.com/restaurant/search"  # Replace with real API endpoint
        params = {"location": location, "cuisine": cuisine, "date": date}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"Restaurant API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling restaurant API: {e}")
        return {}

    async def _fetch_restaurant_details(self, restaurant_id: str) -> dict:
        """
        Fetch detailed restaurant information from an external API.
        """
        api_url = f"https://api.example.com/restaurant/{restaurant_id}/details"  # Replace with real API endpoint
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"Restaurant details API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling restaurant details API: {e}")
        return {}

    async def _fetch_suggestions_api(self, budget: str, cuisine: str) -> list:
        """
        Fetch restaurant suggestions from an external API based on budget and cuisine.
        """
        api_url = "https://api.example.com/restaurant/suggestions"  # Replace with real API endpoint
        params = {"budget": budget, "cuisine": cuisine}
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

    async def _generate_suggestions_via_llm(self, budget: str, cuisine: str) -> list:
        """
        Use Semantic Kernel's LLM (via AzureOpenAIService) to generate restaurant suggestions.
        """
        prompt = (
            f"Generate a JSON object with a 'suggestions' key containing restaurant names that "
            f"match a budget of {budget} and offer {cuisine} cuisine."
        )
        try:
            result = await self.kernel.invoke(prompt)
            data = json.loads(result)
            return data.get("suggestions", [])
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
        return []