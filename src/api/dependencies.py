from typing import List
import logging
from fastapi import Depends
from ..core.config import get_settings
from ..core.orchestrator import Orchestrator
from ..infrastructure.azure_openai import AzureOpenAIService
from ..infrastructure.cosmos_repository import CosmosRepository
from ..infrastructure.flight_service import FlightService
from ..infrastructure.hotel_service import HotelService
from ..infrastructure.restaurant_service import RestaurantService
from ..infrastructure.excursion_service import ExcursionService
from ..agents.flight_agent import FlightAgent
from ..agents.hotel_agent import HotelAgent
from ..agents.restaurant_agent import RestaurantAgent
from ..agents.excursion_agent import ExcursionAgent

def get_logger():
    return logging.getLogger(__name__)

def get_openai_service():
    settings = get_settings()
    return AzureOpenAIService(api_key=settings.azure_openai_api_key, endpoint=settings.azure_openai_endpoint)

def get_cosmos_repository():
    settings = get_settings()
    return CosmosRepository(settings.cosmos_connection_string)

def get_flight_service(openai_service: AzureOpenAIService = Depends(get_openai_service)):
    settings = get_settings()
    return FlightService(api_key=settings.flight_api_key, api_base_url=settings.flight_api_base_url, openai_service=openai_service)

def get_hotel_service(openai_service: AzureOpenAIService = Depends(get_openai_service)):
    settings = get_settings()
    return HotelService(api_key=settings.hotel_api_key, api_base_url=settings.hotel_api_base_url, openai_service=openai_service)

def get_restaurant_service(openai_service: AzureOpenAIService = Depends(get_openai_service)):
    settings = get_settings()
    return RestaurantService(api_key=settings.restaurant_api_key, api_base_url=settings.restaurant_api_base_url, openai_service=openai_service)

def get_excursion_service(openai_service: AzureOpenAIService = Depends(get_openai_service)):
    settings = get_settings()
    return ExcursionService(api_key=settings.excursion_api_key, api_base_url=settings.excursion_api_base_url, openai_service=openai_service)

def get_orchestrator(
    openai_service: AzureOpenAIService = Depends(get_openai_service),
    repository: CosmosRepository = Depends(get_cosmos_repository),
    flight_service: FlightService = Depends(get_flight_service),
    hotel_service: HotelService = Depends(get_hotel_service),
    restaurant_service: RestaurantService = Depends(get_restaurant_service),
    excursion_service: ExcursionService = Depends(get_excursion_service)
) -> Orchestrator:
    flight_agent = FlightAgent(flight_service, openai_service)
    hotel_agent = HotelAgent(hotel_service, openai_service)
    restaurant_agent = RestaurantAgent(restaurant_service, openai_service)
    excursion_agent = ExcursionAgent(excursion_service, openai_service)
    
    return Orchestrator(
        flight_agent=flight_agent,
        hotel_agent=hotel_agent,
        excursion_agent=excursion_agent,
        restaurant_agent=restaurant_agent,
        openai_service=openai_service,
        repository=repository
    )
