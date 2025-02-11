import logging
from ..core.orchestrator import Orchestrator

def get_logger() -> logging.Logger:
    """Return a logger instance for the current module."""
    return logging.getLogger(__name__)

# Single orchestrator instance for the app
orchestrator = Orchestrator()

async def get_orchestrator() -> Orchestrator:
    """Return the global orchestrator instance."""
    return orchestrator