import logging
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..infrastructure.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class FlightSkill:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.azure_service = AzureOpenAIService(kernel)
        
        # Register skill functions with the kernel.
        self.kernel.add_function(self.search_flights)
        self.kernel.add_function(self.get_flight_details)
        self.kernel.add_function(self.suggest_flights)

    @kernel_function(
        description="Search for flights based on origin, destination, and date",
        name="search_flights"
    )
    async def search_flights(self, context: KernelArguments) -> str:
        try:
            origin = context.get("origin", "")
            destination = context.get("destination", "")
            flight_date = context.get("flight_date", "")
            
            if not origin or not destination or not flight_date:
                context["error"] = "Origin, destination, and flight date must be provided."
                return "Please provide origin, destination, and flight date."

            response = f"Found flights from {origin} to {destination} on {flight_date}."
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to search flights: {str(e)}")
            context["error"] = f"Failed to search flights: {str(e)}"
            return "Sorry, an error occurred while searching for flights."

    @kernel_function(
        description="Get detailed information about a specific flight",
        name="get_flight_details"
    )
    async def get_flight_details(self, context: KernelArguments) -> str:
        try:
            flight_id = context.get("flight_id", "")
            if not flight_id:
                context["error"] = "Flight ID must be provided."
                return "Please provide a flight ID."

            response = f"Retrieved details for flight {flight_id}."
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to get flight details: {str(e)}")
            context["error"] = f"Failed to get flight details: {str(e)}"
            return "Sorry, an error occurred while retrieving flight details."

    @kernel_function(
        description="Suggest flights based on user preferences",
        name="suggest_flights"
    )
    async def suggest_flights(self, context: KernelArguments) -> str:
        try:
            travel_class = context.get("travel_class", "")
            budget = context.get("budget", "")
            
            response = f"Based on your preference for {travel_class} class and budget {budget}, here are some flight suggestions."
            context["success"] = "true"
            context["response"] = response
            context["suggestions"] = ["Flight A123", "Flight B456", "Flight C789"]
            return response
            
        except Exception as e:
            logger.error(f"Failed to suggest flights: {str(e)}")
            context["error"] = f"Failed to suggest flights: {str(e)}"
            return "Sorry, an error occurred while generating flight suggestions."