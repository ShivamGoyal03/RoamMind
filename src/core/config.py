import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2023-03-15-preview"  
    cosmos_connection_string: str
    flight_api_key: str
    flight_api_base_url: str
    hotel_api_key: str
    hotel_api_base_url: str
    restaurant_api_key: str
    restaurant_api_base_url: str
    excursion_api_key: str
    excursion_api_base_url: str

    class Config:
        env_file = ".env"  # Load environment variables from a .env file

def get_settings() -> Settings:
    return Settings()
