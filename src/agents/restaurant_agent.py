from typing import List
from ..models.restaurant import Restaurant, Review, Menu
from .base import BaseAgent, AgentRequest, AgentResponse
from ..infrastructure.restaurant_service import RestaurantService
from ..infrastructure.azure_openai import AzureOpenAIService
from ..models.restaurant import RestaurantSearchParams
from ..exceptions import RestaurantNotFoundError
from ..utils.date_helper import parse_date_string
from ..utils.logger import setup_logger, ValidationError

logger = setup_logger(__name__)

class RestaurantAgent(BaseAgent):
    """Agent for handling restaurant-related queries."""
    
    SUPPORTED_INTENTS = {
        "search_restaurants",
        "restaurant_info",
        "check_availability",
        "view_menu",
        "get_recommendations",
        "read_reviews"
    }
    
    def __init__(self, restaurant_service: RestaurantService, openai_service: AzureOpenAIService):
        logger.info("Initializing RestaurantAgent")
        self.restaurant_service = restaurant_service
        self.openai_service = openai_service
        
    async def can_handle(self, intent: str) -> bool:
        return intent.lower() in self.SUPPORTED_INTENTS
        
    async def get_name(self) -> str:
        return "Restaurant Agent"
        
    async def get_description(self) -> str:
        return "I can help you find restaurants, make reservations, view menus, and get dining recommendations."
        
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            intent = request.get_parameter("intent", "").lower()
            logger.info(f"Processing intent: {intent}")
            
            if intent == "search_restaurants":
                return await self._handle_restaurant_search(request)
            elif intent == "restaurant_info":
                return await self._handle_restaurant_info(request)
            elif intent == "check_availability":
                return await self._handle_availability_check(request)
            elif intent == "view_menu":
                return await self._handle_menu_request(request)
            elif intent == "get_recommendations":
                return await self._handle_recommendations(request)
            elif intent == "read_reviews":
                return await self._handle_reviews_request(request)
                
            return AgentResponse(
                success=False,
                response="I'm not sure how to help with that. Would you like to search for restaurants?",
                suggestions=["Search restaurants", "Get recommendations", "View popular places"]
            )
            
        except ValidationError as e:
            logger.error(f"Validation error processing restaurant request: {e}. User Input: {request.input}")
            return AgentResponse(success=False, response="Invalid input. Please check your request and try again.", suggestions=["Try again", "Check your input"])
        except (RestaurantNotFoundError) as e:
            logger.error(f"Error during API interaction or restaurant not found: {e}. User Input: {request.input}, Intent: {request.get_parameter('intent', 'N/A')}")
            return AgentResponse(success=False, response="There was a problem processing your request. Please try again later.", suggestions=["Try again"])
        except Exception as e:
            logger.exception(f"Unexpected error processing restaurant request: {e}. User Input: {request.input}")
            return AgentResponse(success=False, response="Sorry, an unexpected error occurred. Please try again later.", suggestions=[])
        
            
    async def _handle_restaurant_search(self, request: AgentRequest) -> AgentResponse:
        search_info = await self.openai_service.extract_restaurant_information(
            request.input,
            request.context
        )
        
        try:
            search_params = RestaurantSearchParams(**search_info)
            restaurants = await self.restaurant_service.search_restaurants(search_params)
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Failed to search restaurants: {str(e)}",
                suggestions=["Try different cuisine", "Change location"]
            )
            
        if not restaurants:
            return AgentResponse(
                success=True,
                response="I couldn't find any restaurants matching your criteria. Would you like to try different options?",
                suggestions=[
                    "Try different cuisine",
                    "Expand search area",
                    "Change price range"
                ]
            )
            
        return AgentResponse(
            success=True,
            response=self._format_restaurant_results(restaurants),
            data={"restaurants": [r.to_dict() for r in restaurants]},
            suggestions=[
                "View menu",
                "Make reservation",
                "See reviews"
            ]
        )
        
    async def _handle_restaurant_info(self, request: AgentRequest) -> AgentResponse:
        """Handle requests for detailed restaurant information."""
        restaurant_id = request.get_parameter("restaurant_id")
        
        if not restaurant_id:
            return AgentResponse(
                success=False,
                response="Please specify which restaurant you'd like to know more about.",
                suggestions=["Search restaurants", "View popular places"]
            )
            
        try:
            restaurant = await self.restaurant_service.get_restaurant_details(restaurant_id)
            return AgentResponse(
                success=True,
                response=self._format_restaurant_details(restaurant),
                data={"restaurant": restaurant.to_dict()},
                suggestions=["Make reservation", "View menu", "Read reviews"]
            )
        except RestaurantNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that restaurant.",
                suggestions=["Search restaurants", "View popular places"]
            )
            
    async def _handle_menu_request(self, request: AgentRequest) -> AgentResponse:
        """Handle requests to view restaurant menus."""
        restaurant_id = request.get_parameter("restaurant_id")
        
        if not restaurant_id:
            return AgentResponse(
                success=False,
                response="Please specify which restaurant's menu you'd like to see.",
                suggestions=["Search restaurants", "View popular places"]
            )
        
        try:
            menu = await self.restaurant_service.get_menu(restaurant_id)
            return AgentResponse(
                success=True,
                response=self._format_menu(menu),
                data={"menu": menu.to_dict()},
                suggestions=[
                    "Make reservation",
                    "View reviews",
                    "Check availability"
                ]
            )
        except RestaurantNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that restaurant.",
                suggestions=["Search restaurants", "View popular places"]
            )
        
    async def _handle_recommendations(self, request: AgentRequest) -> AgentResponse:
        """Handle restaurant recommendation requests."""
        preferences = await self.openai_service.extract_dining_preferences(
            request.input,
            request.context
        )
        
        try:
            recommendations = await self.restaurant_service.get_recommendations(preferences)
            
            if not recommendations:
                return AgentResponse(
                    success=True,
                    response="I couldn't find any restaurants matching your preferences. Would you like to try different criteria?",
                    suggestions=[
                        "Try different cuisine",
                        "Change location",
                        "Adjust price range"
                    ]
                )
            
            return AgentResponse(
                success=True,
                response=self._format_recommendations(recommendations),
                data={"recommendations": [r.to_dict() for r in recommendations]},
                suggestions=[
                    "View menu",
                    "Make reservation",
                    "See more options"
                ]
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Error getting recommendations: {str(e)}",
                suggestions=["Try again", "Search restaurants"]
            )
        
    async def _handle_reviews_request(self, request: AgentRequest) -> AgentResponse:
        """Handle requests to read restaurant reviews."""
        restaurant_id = request.get_parameter("restaurant_id")
        
        if not restaurant_id:
            return AgentResponse(
                success=False,
                response="Please specify which restaurant's reviews you'd like to see.",
                suggestions=["Search restaurants", "View popular places"]
            )
        
        try:
            reviews = await self.restaurant_service.get_reviews(restaurant_id)
            return AgentResponse(
                success=True,
                response=self._format_reviews(reviews),
                data={"reviews": [r.to_dict() for r in reviews]},
                suggestions=[
                    "Make reservation",
                    "View menu",
                    "Check availability"
                ]
            )
        except RestaurantNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that restaurant.",
                suggestions=["Search restaurants", "View popular places"]
            )
        
    async def _handle_availability_check(self, request: AgentRequest) -> AgentResponse:
        """Handle restaurant availability check requests."""
        restaurant_id = request.get_parameter("restaurant_id")
        date_str = request.get_parameter("date")
        party_size = request.get_parameter("party_size", 2)
        
        # Validate required parameters
        if not all([restaurant_id, date_str]):
            return AgentResponse(
                success=False,
                response="Please provide the restaurant and desired date to check availability.",
                suggestions=["Search restaurants", "View popular places"]
            )
        
        try:
            # Parse date
            date = parse_date_string(date_str)
            if not date:
                return AgentResponse(
                    success=False,
                    response="Please provide a valid date format.",
                    suggestions=["Try different date", "Search restaurants"]
                )
            
            # Check availability using restaurant service
            availability = await self.restaurant_service.check_availability(
                restaurant_id=restaurant_id,
                date=date,
                party_size=party_size
            )
            
            if availability.get("is_available"):
                restaurant = await self.restaurant_service.get_restaurant_details(restaurant_id)
                
                return AgentResponse(
                    success=True,
                    response=(
                        f"Good news! {restaurant.name} has availability for {party_size} "
                        f"people on {date.strftime('%B %d')}.\n"
                        f"Available times: {', '.join(availability.get('available_times', []))}\n"
                        f"{availability.get('special_notes', '')}"
                    ),
                    data={
                        "availability": availability,
                        "restaurant": restaurant.to_dict()
                    },
                    suggestions=[
                        "Make reservation",
                        "View menu",
                        "Read reviews"
                    ]
                )
            else:
                return AgentResponse(
                    success=True,
                    response=(
                        f"Sorry, the restaurant is not available for {party_size} people "
                        f"on {date.strftime('%B %d')}.\n"
                        f"{availability.get('alternative_suggestions', '')}"
                    ),
                    data={"availability": availability},
                    suggestions=[
                        "Check different time",
                        "Try another date",
                        "View similar restaurants"
                    ]
                )
            
        except RestaurantNotFoundError:
            return AgentResponse(
                success=False,
                response="Sorry, I couldn't find that restaurant.",
                suggestions=["Search restaurants", "View popular places"]
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                response=f"Error checking availability: {str(e)}",
                suggestions=["Try again", "Search different restaurants"]
            )
        
    def _format_restaurant_results(self, restaurants: List[Restaurant]) -> str:
        """Format restaurant search results into a readable message."""
        if not restaurants:
            return "No restaurants found."
            
        response = "Here are the restaurants I found:\n\n"
        for i, restaurant in enumerate(restaurants, 1):
            response += (
                f"{i}. {restaurant.name} {restaurant.price_range}\n"
                f"   Cuisine: {', '.join(restaurant.cuisine_type)}\n"
                f"   Rating: {restaurant.rating}/5 ({restaurant.review_count} reviews)\n"
                f"   Location: {restaurant.address}\n\n"
            )
        
        return response
        
    def _format_restaurant_details(self, restaurant: Restaurant) -> str:
        """Format detailed restaurant information."""
        return (
            f"🍽️ {restaurant.name} {restaurant.price_range}\n\n"
            f"📍 {restaurant.address}\n"
            f"Cuisine: {', '.join(restaurant.cuisine_type)}\n"
            f"Rating: {restaurant.rating}/5 ({restaurant.review_count} reviews)\n\n"
            f"Description:\n{restaurant.description}\n\n"
            f"Features:\n" + "\n".join(f"• {feature}" for feature in restaurant.features) + "\n\n"
            f"Dietary Options:\n" + "\n".join(f"• {option}" for option in restaurant.dietary_options) + "\n\n"
            f"Opening Hours:\n" + "\n".join(
                f"• {day}: {', '.join(hours)}"
                for day, hours in restaurant.opening_hours.items()
            )
        )
        
    def _format_menu(self, menu: Menu) -> str:
        """Format restaurant menu into readable text."""
        response = f"🍽️ Menu for {menu.restaurant_name}\n\n"
        
        for category in menu.categories:
            response += f"📋 {category.name}\n"
            for item in category.items:
                response += (
                    f"• {item.name} - ${item.price:.2f}\n"
                    f"  {item.description}\n"
                )
            response += "\n"
        
        return response
        
    def _format_recommendations(self, recommendations: List[Restaurant]) -> str:
        """Format restaurant recommendations into readable text."""
        response = "Here are some restaurants you might like:\n\n"
        
        for i, restaurant in enumerate(recommendations, 1):
            response += (
                f"{i}. {restaurant.name} {restaurant.price_range}\n"
                f"   Cuisine: {', '.join(restaurant.cuisine_type)}\n"
                f"   Rating: {restaurant.rating}/5 ({restaurant.review_count} reviews)\n"
                f"   Known for: {restaurant.highlights}\n\n"
            )
        
        return response
        
    def _format_reviews(self, reviews: List[Review]) -> str:
        """Format restaurant reviews into readable text."""
        response = "Recent Reviews:\n\n"
        
        for review in reviews[:5]:  
            response += (
                f"⭐ {review.rating}/5 - {review.author}\n"
                f"{review.comment}\n"
                f"Date: {review.date.strftime('%B %d, %Y')}\n\n"
            )
        
        return response
