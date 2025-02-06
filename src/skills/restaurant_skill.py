import logging
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..infrastructure.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class RestaurantSkill:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.azure_service = AzureOpenAIService(kernel)
        
        # Register skill functions with the kernel.
        self.kernel.add_function(self.search_restaurants)
        self.kernel.add_function(self.get_restaurant_details)
        self.kernel.add_function(self.suggest_restaurants)

    @kernel_function(
        description="Search for restaurants based on location and dining preferences",
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

            response = f"Found restaurants in {location} serving {cuisine} cuisine on {date}."
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to search restaurants: {str(e)}")
            context["error"] = f"Failed to search restaurants: {str(e)}"
            return "Sorry, an error occurred while searching for restaurants."

    @kernel_function(
        description="Get detailed information about a specific restaurant",
        name="get_restaurant_details"
    )
    async def get_restaurant_details(self, context: KernelArguments) -> str:
        try:
            restaurant_id = context.get("restaurant_id", "")
            if not restaurant_id:
                context["error"] = "Restaurant ID must be provided."
                return "Please provide a restaurant ID."

            response = f"Retrieved details for restaurant {restaurant_id}."
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to get restaurant details: {str(e)}")
            context["error"] = f"Failed to get restaurant details: {str(e)}"
            return "Sorry, an error occurred while retrieving restaurant details."

    @kernel_function(
        description="Suggest restaurants based on user dining preferences",
        name="suggest_restaurants"
    )
    async def suggest_restaurants(self, context: KernelArguments) -> str:
        try:
            budget = context.get("budget", "")
            cuisine = context.get("cuisine", "")
            
            response = f"Based on your budget ({budget}) and preferred cuisine ({cuisine}), here are some restaurant suggestions."
            context["success"] = "true"
            context["response"] = response
            context["suggestions"] = ["The Gourmet Kitchen", "City Bites", "Flavor Fiesta"]
            return response
            
        except Exception as e:
            logger.error(f"Failed to suggest restaurants: {str(e)}")
            context["error"] = f"Failed to suggest restaurants: {str(e)}"
            return "Sorry, an error occurred while generating restaurant suggestions."