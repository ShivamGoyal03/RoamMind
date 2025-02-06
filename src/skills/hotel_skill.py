import logging
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..infrastructure.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class HotelSkill:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.azure_service = AzureOpenAIService(kernel)
        
        # Register skill functions with the kernel.
        self.kernel.add_function(self.search_hotels)
        self.kernel.add_function(self.get_hotel_details)
        self.kernel.add_function(self.suggest_hotels)

    @kernel_function(
        description="Search for hotels based on location and preferences",
        name="search_hotels"
    )
    async def search_hotels(self, context: KernelArguments) -> str:
        try:
            location = context.get("location", "")
            check_in_date = context.get("check_in_date", "")
            check_out_date = context.get("check_out_date", "")
            
            if not location or not check_in_date or not check_out_date:
                context["error"] = "Location, check-in and check-out dates must be provided."
                return "Please provide location and complete booking dates."

            response = f"Found hotels in {location} available from {check_in_date} to {check_out_date}."
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to search hotels: {str(e)}")
            context["error"] = f"Failed to search hotels: {str(e)}"
            return "Sorry, an error occurred while searching for hotels."

    @kernel_function(
        description="Get detailed information about a specific hotel",
        name="get_hotel_details"
    )
    async def get_hotel_details(self, context: KernelArguments) -> str:
        try:
            hotel_id = context.get("hotel_id", "")
            if not hotel_id:
                context["error"] = "Hotel ID must be provided."
                return "Please provide a hotel ID."

            response = f"Retrieved details for hotel {hotel_id}."
            context["success"] = "true"
            context["response"] = response
            return response
            
        except Exception as e:
            logger.error(f"Failed to get hotel details: {str(e)}")
            context["error"] = f"Failed to get hotel details: {str(e)}"
            return "Sorry, an error occurred while retrieving hotel details."

    @kernel_function(
        description="Suggest hotels based on user preferences",
        name="suggest_hotels"
    )
    async def suggest_hotels(self, context: KernelArguments) -> str:
        try:
            star_rating = context.get("star_rating", "")
            amenities = context.get("amenities", "")
            
            response = f"Based on your preferences for a {star_rating}-star hotel with amenities like {amenities}, here are some suggestions."
            context["success"] = "true"
            context["response"] = response
            context["suggestions"] = ["Grand Plaza", "City Inn", "Comfort Stay"]
            return response
            
        except Exception as e:
            logger.error(f"Failed to suggest hotels: {str(e)}")
            context["error"] = f"Failed to suggest hotels: {str(e)}"
            return "Sorry, an error occurred while generating hotel suggestions."