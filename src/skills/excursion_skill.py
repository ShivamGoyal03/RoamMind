import json
import logging
import aiohttp
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..infrastructure.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class ExcursionSkill:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        # Initialize the Azure service using the kernel.
        self.azure_service = AzureOpenAIService(kernel)
        
        # Register skill functions with the kernel.
        self.kernel.add_function(self.search_excursions)
        self.kernel.add_function(self.get_excursion_details)
        self.kernel.add_function(self.suggest_excursions)

    @kernel_function(
        description="Search for excursions based on location and activity preferences using external APIs.",
        name="search_excursions"
    )
    async def search_excursions(self, context: KernelArguments) -> str:
        try:
            location = context.get("location", "")
            activity = context.get("activity", "")
            date = context.get("date", "")
            
            if not location or not activity:
                context["error"] = "Location and activity must be provided."
                return "Please provide both location and type of activity to search for excursions."

            # Attempt to call an external excursion search API.
            api_response = await self._fetch_excursion_data(location, activity, date)
            if api_response and "response" in api_response:
                response = api_response["response"]
            else:
                response = f"Found excursions in {location} for {activity} on {date}."
                
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to search excursions: {str(e)}")
            context["error"] = f"Failed to search excursions: {str(e)}"
            return "Sorry, an error occurred while searching for excursions."

    @kernel_function(
        description="Get detailed information about a specific excursion from external APIs.",
        name="get_excursion_details"
    )
    async def get_excursion_details(self, context: KernelArguments) -> str:
        try:
            excursion_id = context.get("excursion_id", "")
            if not excursion_id:
                context["error"] = "Excursion ID must be provided."
                return "Please provide an excursion ID."

            # Call an external API to get excursion details.
            details = await self._fetch_excursion_details(excursion_id)
            if details and "details" in details:
                response = details["details"]
            else:
                response = f"Retrieved details for excursion {excursion_id}."
                
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to get excursion details: {str(e)}")
            context["error"] = f"Failed to get excursion details: {str(e)}"
            return "Sorry, an error occurred while retrieving excursion details."

    @kernel_function(
        description="Suggest excursions based on user preferences using external APIs and LLM fallback.",
        name="suggest_excursions"
    )
    async def suggest_excursions(self, context: KernelArguments) -> str:
        try:
            budget = context.get("budget", "")
            activity = context.get("activity", "")
            
            # Attempt to get suggestions via external API.
            api_suggestions = await self._fetch_suggestions_api(budget, activity)
            
            # If no suggestions are returned via the API, fall back to the LLM.
            if not api_suggestions:
                llm_suggestions = await self._generate_suggestions_via_llm(budget, activity)
                suggestions = llm_suggestions
            else:
                suggestions = api_suggestions
            
            response = f"Based on  budget ({budget}) and preferred activity ({activity}), here are some excursion suggestions."
            context["success"] = "true"
            context["response"] = response
            context["suggestions"] = suggestions
            return response
            
        except Exception as e:
            logger.error(f"Failed to suggest excursions: {str(e)}")
            context["error"] = f"Failed to suggest excursions: {str(e)}"
            return "Sorry, an error occurred while generating excursion suggestions."

    async def _fetch_excursion_data(self, location: str, activity: str, date: str) -> dict:
        """
        Fetch excursion search results from an external API.
        """
        api_url = "https://api.example.com/excursion/search"  # Replace with  real API endpoint
        params = {"location": location, "activity": activity, "date": date}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"Excursion API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling excursion API: {e}")
        return {}

    async def _fetch_excursion_details(self, excursion_id: str) -> dict:
        """
        Fetch detailed excursion information from an external API.
        """
        api_url = f"https://api.example.com/excursion/{excursion_id}/details"  # Replace with  real API endpoint
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"Excursion details API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling excursion details API: {e}")
        return {}

    async def _fetch_suggestions_api(self, budget: str, activity: str) -> list:
        """
        Fetch excursion suggestions from an external API based on budget and activity.
        """
        api_url = "https://api.example.com/excursion/suggestions"  # Replace with  real API endpoint
        params = {"budget": budget, "activity": activity}
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

    async def _generate_suggestions_via_llm(self, budget: str, activity: str) -> list:
        """
        Use Semantic Kernel's LLM (via AzureOpenAIService) to generate excursion suggestions.
        """
        prompt = (
            f"Generate a JSON object with a 'suggestions' key containing excursion names that "
            f"match a budget of {budget} and offer activities related to {activity}."
        )
        try:
            result = await self.kernel.invoke(prompt)
            data = json.loads(result)
            return data.get("suggestions", [])
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
        return []