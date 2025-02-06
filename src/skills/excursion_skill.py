import logging
from typing import Any
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from ..infrastructure.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class ExcursionSkill:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.azure_service = AzureOpenAIService(kernel)
        self.skill_name = "ExcursionSkill"
        
        # Register the functions with the kernel.
        self.kernel.add_function(self.search_excursions)
        self.kernel.add_function(self.get_excursion_details)
        self.kernel.add_function(self.suggest_excursions)

    @kernel_function(
        description="Search for excursions based on location and preferences",
        name="search_excursions"
    )
    async def search_excursions(self, context: KernelArguments) -> str:
        try:
            location = context.get("location", "")
            date = context.get("date", "")
            preferences = context.get("preferences", "")

            if not location or not date:
                # Record error in context by setting an error field.
                context["error"] = "Location and date must be provided."
                return "Please provide both location and date."

            response = f"Found excursions in {location} for {date} matching: {preferences}"
            # Update context with output values.
            context["success"] = "true"
            context["response"] = response
            return response

        except Exception as e:
            logger.error(f"Failed to search excursions: {str(e)}")
            context["error"] = f"Failed to search excursions: {str(e)}"
            return "Sorry, I couldn't find any excursions matching your criteria."

    @kernel_function(
        description="Get detailed information about a specific excursion",
        name="get_excursion_details"
    )
    async def get_excursion_details(self, context: KernelArguments) -> str:
        try:
            excursion_id = context.get("excursion_id", "")
            if not excursion_id:
                context["error"] = "Excursion ID must be provided."
                return "Please provide an excursion ID."

            response = f"Retrieved details for excursion {excursion_id}"
            context["success"] = "true"
            context["response"] = response
            return response

        except Exception as e:
            logger.error(f"Failed to get excursion details: {str(e)}")
            context["error"] = f"Failed to get excursion details: {str(e)}"
            return "Sorry, I couldn't retrieve the excursion details."

    @kernel_function(
        description="Suggest excursions based on user preferences",
        name="suggest_excursions"
    )
    async def suggest_excursions(self, context: KernelArguments) -> str:
        try:
            interests = context.get("interests", "")
            budget = context.get("budget", "")

            response = f"Based on your interests ({interests}) and budget ({budget}), here are some suggestions..."
            context["success"] = "true"
            context["response"] = response
            context["suggestions"] = ["City Tour", "Adventure Trek", "Cultural Visit"]
            return response

        except Exception as e:
            logger.error(f"Failed to suggest excursions: {str(e)}")
            context["error"] = f"Failed to suggest excursions: {str(e)}"
            return "Sorry, I couldn't generate excursion suggestions."

    async def handle_request(self, user_input: str, conversation) -> dict:
        try:
            excursion_info = await self.azure_service.extract_excursion_information(user_input, conversation.context)
            enhanced_info = await self.azure_service.enhance_excursion_details(excursion_info)
            return {
                "success": True,
                "response": f"Excursion information extracted: {enhanced_info}"
            }
        except Exception as e:
            logger.error(f"Error handling excursion request: {str(e)}")
            return {
                "success": False,
                "response": "Failed to handle excursion request."
            }