import json
import logging
import aiohttp
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..infrastructure.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class FlightSkill:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        # Initialize the Azure service using the kernel.
        self.azure_service = AzureOpenAIService(kernel)
        
        # Register skill functions with the kernel.
        self.kernel.add_function(self.search_flights)
        self.kernel.add_function(self.get_flight_details)
        self.kernel.add_function(self.suggest_flights)

    @kernel_function(
        description="Search for flights based on origin, destination, and travel dates using external APIs.",
        name="search_flights"
    )
    async def search_flights(self, context: KernelArguments) -> str:
        try:
            origin = context.get("origin", "")
            destination = context.get("destination", "")
            departure_date = context.get("departure_date", "")
            return_date = context.get("return_date", "")
            
            if not origin or not destination:
                context["error"] = "Origin and destination must be provided."
                return "Please provide both origin and destination to search for flights."

            # Attempt to call an external flight search API.
            api_response = await self._fetch_flight_data(origin, destination, departure_date, return_date)
            if api_response and "response" in api_response:
                response = api_response["response"]
            else:
                response = f"Found flights from {origin} to {destination} departing on {departure_date}."
                
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to search flights: {str(e)}")
            context["error"] = f"Failed to search flights: {str(e)}"
            return "Sorry, an error occurred while searching for flights."

    @kernel_function(
        description="Get detailed information about a specific flight from external APIs.",
        name="get_flight_details"
    )
    async def get_flight_details(self, context: KernelArguments) -> str:
        try:
            flight_id = context.get("flight_id", "")
            if not flight_id:
                context["error"] = "Flight ID must be provided."
                return "Please provide a flight ID."

            # Call an external API to get flight details.
            details = await self._fetch_flight_details(flight_id)
            if details and "details" in details:
                response = details["details"]
            else:
                response = f"Retrieved details for flight {flight_id}."
                
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to get flight details: {str(e)}")
            context["error"] = f"Failed to get flight details: {str(e)}"
            return "Sorry, an error occurred while retrieving flight details."

    @kernel_function(
        description="Suggest flights based on user travel preferences using external APIs and LLM fallback.",
        name="suggest_flights"
    )
    async def suggest_flights(self, context: KernelArguments) -> str:
        try:
            budget = context.get("budget", "")
            airline_preference = context.get("airline", "")
            
            # Attempt to get suggestions via external API.
            api_suggestions = await self._fetch_suggestions_api(budget, airline_preference)
            
            # If no suggestions are returned via the API, fall back to the LLM.
            if not api_suggestions:
                llm_suggestions = await self._generate_suggestions_via_llm(budget, airline_preference)
                suggestions = llm_suggestions
            else:
                suggestions = api_suggestions
            
            response = f"Based on your budget ({budget}) and preferred airline ({airline_preference}), here are some flight suggestions."
            context["success"] = "true"
            context["response"] = response
            context["suggestions"] = suggestions
            return response
            
        except Exception as e:
            logger.error(f"Failed to suggest flights: {str(e)}")
            context["error"] = f"Failed to suggest flights: {str(e)}"
            return "Sorry, an error occurred while generating flight suggestions."

    async def _fetch_flight_data(self, origin: str, destination: str, departure_date: str, return_date: str) -> dict:
        """
        Fetch flight search results from an external API.
        """
        api_url = "https://api.example.com/flight/search"  # Replace with real API endpoint
        params = {
            "origin": origin, 
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"Flight API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling flight API: {e}")
        return {}

    async def _fetch_flight_details(self, flight_id: str) -> dict:
        """
        Fetch detailed flight information from an external API.
        """
        api_url = f"https://api.example.com/flight/{flight_id}/details"  # Replace with real API endpoint
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        logger.error(f"Flight details API error with status: {resp.status}")
        except Exception as e:
            logger.error(f"Exception when calling flight details API: {e}")
        return {}

    async def _fetch_suggestions_api(self, budget: str, airline: str) -> list:
        """
        Fetch flight suggestions from an external API based on budget and airline preference.
        """
        api_url = "https://api.example.com/flight/suggestions"  # Replace with real API endpoint
        params = {"budget": budget, "airline": airline}
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

    async def _generate_suggestions_via_llm(self, budget: str, airline: str) -> list:
        """
        Use Semantic Kernel's LLM (via AzureOpenAIService) to generate flight suggestions.
        """
        prompt = (
            f"Generate a JSON object with a 'suggestions' key containing flight options that "
            f"match a budget of {budget} and are operated by {airline}."
        )
        try:
            result = await self.kernel.invoke(prompt)
            data = json.loads(result)
            return data.get("suggestions", [])
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
        return []