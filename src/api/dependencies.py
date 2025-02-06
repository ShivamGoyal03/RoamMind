import logging
from ..core.config import get_settings
from ..core.orchestrator import Orchestrator
from ..infrastructure.cosmos_repository import CosmosRepository

def get_logger() -> logging.Logger:
    """Return a logger instance for the current module."""
    return logging.getLogger(__name__)

def get_repository() -> CosmosRepository:
    """Return an instance of CosmosRepository based on configuration settings."""
    settings = get_settings()
    return CosmosRepository(settings.cosmos_connection_string)

async def get_orchestrator() -> Orchestrator:
    """
    Create and return an instance of Orchestrator initialized with required dependencies.
    The Orchestrator internally initializes the Semantic Kernel and registers its skill plugins.
    """
    repository = get_repository()
    return Orchestrator(repository)