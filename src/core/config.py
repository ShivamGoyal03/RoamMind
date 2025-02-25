import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2023-03-15-preview"  
    cosmos_connection_string: Optional[str] = None 
    flight_api_key: Optional[str] = None
    flight_api_base_url: Optional[str] = None
    hotel_api_key: Optional[str] = None
    hotel_api_base_url: Optional[str] = None
    restaurant_api_key: Optional[str] = None
    restaurant_api_base_url: Optional[str] = None
    excursion_api_key: Optional[str] = None
    excursion_api_base_url: Optional[str] = None

    # @field_validator('azure_openai_api_key', 'azure_openai_endpoint')
    @classmethod
    def validate_required_fields(cls, v, field):
        if not v:
            raise ValueError(f"{field.name} is required")
        return v

    class Config:
        env_file = ".env"
        # case_sensitive = True

_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
