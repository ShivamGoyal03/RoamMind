import asyncio
import json
import openai
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..core.config import get_settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI.

    This service integrates with Semantic Kernel by accepting a kernel instance on initialization.
    The KernelArguments passed via skills are dict-like objects, so the context parameters here can be used
    directly as dictionaries.
    """

    def __init__(self, kernel):
        # Semantic Kernel instance (not directly used in API calls)
        self.kernel = kernel
        settings = get_settings()
        openai.api_type = "azure"
        openai.api_base = settings.azure_openai_endpoint
        openai.api_version = settings.azure_openai_api_version
        openai.api_key = settings.azure_openai_api_key

    async def enhance_excursion_details(self, api_response: Dict) -> Dict:
        """Enhance excursion details using LLM."""
        prompt = self._create_enhancement_prompt(
            api_response, enhancement_type="excursion details")
        response = await self._get_completion(prompt)
        return self._parse_enhancement_response(response)

    async def validate_excursion_booking(
        self,
        excursion_id: str,
        date: datetime,
        participants: int,
        customer_details: Dict
    ) -> Dict:
        """Validate booking parameters using LLM."""
        prompt = self._create_validation_prompt(
            excursion_id, date, participants, customer_details
        )
        response = await self._get_completion(prompt)
        return self._parse_validation_response(response)

    async def _get_completion(self, prompt: str) -> str:
        """Get completion from Azure OpenAI."""
        try:
            response = await openai.ChatCompletion.acreate(
                engine="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error getting completion: {str(e)}")

    async def determine_intent(self, user_input: str) -> str:
        """Determine the primary intent of the user's message."""
        response = await openai.ChatCompletion.acreate(
            engine="gpt-4",
            messages=[
                {"role": "system", "content": "You are a travel assistant. Determine the primary intent of the user's message."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content

    async def extract_flight_information(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Extracting flight information from user input")
        try:
            prompt = self._create_flight_extraction_prompt(input_text, context)
            response = await self._call_openai(prompt)
            return {
                "origin": response.get("origin"),
                "destination": response.get("destination"),
                "departure_date": response.get("departure_date"),
                "return_date": response.get("return_date"),
                "number_of_passengers": response.get("number_of_passengers", 1),
                "class_preference": response.get("class_preference"),
                "flexible_dates": response.get("flexible_dates", False)
            }
        except Exception as e:
            logger.error(f"Error extracting flight information: {str(e)}")
            raise

    async def extract_hotel_information(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract hotel search parameters from user input."""
        logger.info("Extracting hotel information from user input")
        try:
            prompt = self._create_extraction_prompt(
                "hotel", input_text, context)
            response = await self._call_openai(prompt)
            return {
                "location": response.get("location"),
                "check_in": response.get("check_in"),
                "check_out": response.get("check_out"),
                "guests": response.get("guests", 1),
                "room_type": response.get("room_type"),
                "max_price": response.get("max_price"),
                "amenities": response.get("amenities", []),
                "star_rating": response.get("star_rating")
            }
        except Exception as e:
            logger.error(f"Error extracting hotel information: {str(e)}")
            raise

    async def extract_restaurant_information(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract restaurant search parameters from user input."""
        logger.info("Extracting restaurant information from user input")
        try:
            prompt = self._create_extraction_prompt(
                "restaurant", input_text, context)
            response = await self._call_openai(prompt)
            return {
                "location": response.get("location"),
                "cuisine": response.get("cuisine"),
                "price_range": response.get("price_range"),
                "party_size": response.get("party_size", 2),
                "date_time": response.get("date_time"),
                "dietary_restrictions": response.get("dietary_restrictions", []),
                "atmosphere": response.get("atmosphere")
            }
        except Exception as e:
            logger.error(f"Error extracting restaurant information: {str(e)}")
            raise

    async def extract_excursion_information(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract excursion search parameters from user input."""
        logger.info("Extracting excursion information from user input")
        try:
            prompt = self._create_extraction_prompt(
                "excursion", input_text, context)
            response = await self._call_openai(prompt)
            return {
                "location": response.get("location"),
                "date": response.get("date"),
                "activity_type": response.get("activity_type"),
                "duration": response.get("duration"),
                "participants": response.get("participants", 1),
                "max_price": response.get("max_price"),
                "difficulty_level": response.get("difficulty_level"),
                "includes_transport": response.get("includes_transport", False),
                "accessibility_needs": response.get("accessibility_needs", [])
            }
        except Exception as e:
            logger.error(f"Error extracting excursion information: {str(e)}")
            raise

    def _create_extraction_prompt(self, type: str, input_text: str, context: Dict[str, Any]) -> str:
        """Create a prompt for information extraction."""
        logger.debug(f"Creating {type} extraction prompt")
        base_prompt = f"Extract {type} information from the following text:\n\n{input_text}\n\n"
        if context.get("user_preferences"):
            base_prompt += f"Consider user preferences: {
                context['user_preferences']}\n"
        if context.get("location"):
            base_prompt += f"Current location: {context['location']}\n"
        return base_prompt

    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Make an actual call to Azure OpenAI API."""
        try:
            response = await openai.ChatCompletion.acreate(
                engine="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a travel assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse OpenAI response as JSON")
            raise
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise

    async def _call_openai_with_retry(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        for attempt in range(max_retries):
            try:
                return await self._call_openai(prompt)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def enhance_search_results(self, results: List[Dict], context: Dict[str, Any]) -> List[Dict]:
        """Enhance search results with personalized recommendations."""
        logger.info("Enhancing search results with AI")
        try:
            prompt = self._create_enhancement_prompt(results, context)
            enhanced_results = await self._call_openai(prompt)
            return enhanced_results
        except Exception as e:
            logger.error(f"Error enhancing search results: {str(e)}")
            return results

    def _create_enhancement_prompt(self, data: Any, context: Optional[Dict[str, Any]] = None, enhancement_type: str = "details") -> str:
        """
        Construct a prompt for LLM to enhance the data.

        Parameters:
          data: The raw data (could be search results, details, availability, etc.).
          context: Additional context, e.g., search parameters.
          enhancement_type: Indicates what is being enhanced; "search results", "details", or "availability".

        Returns:
          A prompt string instructing the LLM to return clear, detailed JSON data.
        """
        prompt = f"Enhance the following {enhancement_type} information to be more clear, detailed, and user-friendly. Please return valid JSON.\n"
        prompt += "Data:\n" + json.dumps(data, indent=2)
        if context:
            prompt += "\nContext:\n" + json.dumps(context, indent=2)
        return prompt

    def _parse_enhancement_response(self, response: str) -> Any:
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}. Raw response: {response}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error parsing LLM response: {e}. Raw response: {response}")
            return None

    async def enhance_hotel_results(self, hotels: List[Dict], search_params: Dict) -> List[Dict]:
        try:
            prompt = self._create_enhancement_prompt(
                hotels, context=search_params)
            response = await self._call_openai(prompt)
            return response if isinstance(response, list) else hotels
        except Exception as e:
            logger.error(f"Error enhancing hotel results: {str(e)}")
            return hotels

    async def enhance_hotel_details(self, hotel_data: Dict) -> Dict:
        """Enhance hotel details using LLM."""
        prompt = self._create_enhancement_prompt(
            hotel_data, enhancement_type="hotel details")
        response = await self._call_openai(prompt)
        enhanced = self._parse_enhancement_response(response)
        if isinstance(enhanced, dict):
            return enhanced
        return hotel_data

    async def enhance_hotel_availability(
        self,
        availability: Dict,
        hotel_id: str,
        room_id: str,
        check_in: datetime,
        check_out: datetime,
        guests: int
    ) -> Dict:
        """Enhance hotel availability information using LLM."""
        context = {
            "hotel_id": hotel_id,
            "room_id": room_id,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guests": guests
        }
        prompt = self._create_enhancement_prompt(
            availability, context=context, enhancement_type="hotel availability")
        response = await self._call_openai(prompt)
        enhanced = self._parse_enhancement_response(response)
        if isinstance(enhanced, dict):
            return enhanced
        return availability

    def _create_flight_extraction_prompt(self, user_input: str, context: Dict) -> str:
        prompt = f"""
Extract flight search parameters from the following user input. Return a JSON object with the following fields: origin, destination, departure_date, return_date (optional), number_of_passengers, class_preference (optional), flexible_dates (boolean, default False). If a field cannot be determined, omit it from the JSON response.

User Input: {user_input}
Context: {json.dumps(context)}

Example Response (for "flights from NYC to London on March 15"):
{{"origin": "NYC", "destination": "London", "departure_date": "2024-03-15"}}

Example Response (for "show me flights to Paris next week"):
{{"destination": "Paris"}}

Response:
"""
        return prompt

    def _create_validation_prompt(self, excursion_id: str, date: datetime, participants: int, customer_details: Dict) -> str:
        """Create a prompt for validating excursion booking parameters."""
        prompt = f"""
Validate the following excursion booking parameters. Return a JSON object with fields 'is_valid' (boolean) and 'reason' (string, explaining why it's invalid if is_valid is False).

Excursion ID: {excursion_id}
Date: {date.isoformat()}
Participants: {participants}
Customer Details: {json.dumps(customer_details)}

Example of valid response:
{{"is_valid": true}}

Example of invalid response:
{{"is_valid": false, "reason": "The excursion is not available on the selected date."}}

Response:
"""
        return prompt

    def _parse_validation_response(self, response: str) -> Dict:
        """Parse the LLM's validation response."""
        try:
            data = json.loads(response)
            if not isinstance(data, dict) or "is_valid" not in data:
                raise ValueError("Invalid response format")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation response as JSON: {e}. Raw response: {response}")
            return {"is_valid": False, "reason": "Error parsing LLM response"}
        except ValueError as e:
            logger.error(f"Invalid validation response format: {e}. Raw response: {response}")
            return {"is_valid": False, "reason": "Invalid response format"}
        except Exception as e:
            logger.exception(f"Unexpected error parsing validation response: {e}. Raw response: {response}")
            return {"is_valid": False, "reason": "Unexpected error"}

    async def enhance_excursion_results(self, excursions: List[Dict], search_params: Dict) -> List[Dict]:
        """Enhance excursion search results using LLM."""
        prompt = self._create_enhancement_prompt(
            excursions, context=search_params, enhancement_type="excursion search results")
        response = await self._call_openai(prompt)
        enhanced = self._parse_enhancement_response(response)
        if isinstance(enhanced, list):
            return enhanced
        return excursions

    async def enhance_excursion_categories(self, categories: List[str], location: str) -> List[str]:
        """Enhance excursion categories recommendations using LLM."""
        context = {"location": location}
        prompt = f"Given the location {location}, enhance the following excursion categories: {
            json.dumps(categories)}. Return the result as a JSON list."
        response = await self._call_openai(prompt)
        try:
            enhanced = json.loads(response)
            if isinstance(enhanced, list):
                return enhanced
        except json.JSONDecodeError:
            logger.error(
                "Failed to parse enhancement response for excursion categories.")
        return categories

    async def enhance_availability_response(self, availability: Dict, excursion_id: str, date: datetime, participants: int) -> Dict:
        """Enhance availability response with LLM suggestions."""
        logger.info("Enhancing availability response with LLM")
        prompt = (f"Enhance the following availability information for excursion {excursion_id} "
                  f"on {date.isoformat()} for {participants} participants: {availability}")
        enhanced = await self._call_openai(prompt)
        if isinstance(enhanced, dict):
            return enhanced
        return availability

    async def enhance_flight_results(self, flights: List[Dict], search_params: Dict) -> List[Dict]:
        try:
            prompt = self._create_flight_results_enhancement_prompt(
                flights, search_params)
            logger.info(f"Enhance Flight Results Prompt: {prompt}")  # Log the prompt
            enhanced_flights = await self._call_openai_with_retry(prompt)
            # Log the enhanced results
            logger.info(f"Enhanced Flight Results: {enhanced_flights}")
            if not isinstance(enhanced_flights, list):
                logger.warning(f"LLM response is not a list: {enhanced_flights}")
                return flights  # Fallback if response is not a list
            return enhanced_flights
        except Exception as e:
            logger.exception(f"Error enhancing flight results: {e}")
            return flights  # Fallback if error occurs

    def _create_flight_results_enhancement_prompt(self, flights: List[Dict], search_params: Dict) -> str:
        prompt = f"""
Enhance the following flight search results to be more user-friendly. Provide a concise summary for each flight, highlighting key details such as airline, departure/arrival times, and price. Return the results as a JSON array.

Search Parameters: {json.dumps(search_params, indent=2)}
Flights: {json.dumps(flights, indent=2)}
"""
        return prompt

    async def enhance_flight_details(self, flight_data: Dict) -> Dict:
        """Enhance detailed flight information using LLM."""
        prompt = self._create_enhancement_prompt(
            flight_data, enhancement_type="details")
        response = await self._call_openai(prompt)
        enhanced = self._parse_enhancement_response(response)
        if isinstance(enhanced, dict):
            return enhanced
        return flight_data

    async def enhance_flight_availability(
        self,
        availability: Dict,
        flight_id: str,
        seats: int,
        seat_class: Optional[str] = None
    ) -> Dict:
        """Enhance flight availability information using LLM."""
        context = {"flight_id": flight_id,"seats": seats, "seat_class": seat_class}
        prompt = self._create_enhancement_prompt(
            availability, context=context, enhancement_type="availability")
        response = await self._call_openai(prompt)
        enhanced = self._parse_enhancement_response(response)
        if isinstance(enhanced, dict):
            return enhanced
        return availability

    async def enhance_menu_details(self, menu_data: Dict, restaurant_id: str) -> Dict:
        """Enhance menu details with descriptions and recommendations using LLM."""
        prompt = f"Enhance the following menu details for restaurant ID {restaurant_id}: {json.dumps(menu_data)}"
        response = await self._call_openai(prompt)
        enhanced = self._parse_enhancement_response(response)
        return enhanced if isinstance(enhanced, dict) else menu_data

    async def analyze_restaurant_reviews(self, reviews: List[Dict], restaurant_id: str) -> Dict:
        """Analyze restaurant reviews with LLM to provide insights and summaries."""
        prompt = f"Analyze the following reviews for restaurant ID {restaurant_id}: {json.dumps(reviews)}"
        response = await self._call_openai(prompt)
        enhanced = self._parse_enhancement_response(response)
        return enhanced if isinstance(enhanced, dict) else {"reviews": reviews, "summary": "No analysis available."}

    async def enhance_restaurant_recommendations(self, recommendations: List[Dict], preferences: Optional[Dict] = None) -> List[Dict]:
        """Enhance restaurant recommendations using LLM."""
        prompt = f"Enhance the following restaurant recommendations based on preferences: {json.dumps(recommendations)} with preferences: {json.dumps(preferences)}"
        response = await self._call_openai(prompt)
        enhanced = self._parse_enhancement_response(response)
        return enhanced if isinstance(enhanced, list) else recommendations

    async def analyze_user_input(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """Analyze user input to determine intent and extract parameters."""
        try:
            response = await openai.ChatCompletion.acreate(
                engine="gpt-4",
                messages=[
                    {"role": "system", "content": "Analyze travel-related user input."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error analyzing user input: {str(e)}")
            raise
