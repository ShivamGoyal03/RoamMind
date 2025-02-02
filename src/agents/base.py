from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pydantic import BaseModel
from ..core.models import ConversationContext
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class AgentRequest(BaseModel):
    input: str
    context: ConversationContext
    parameters: Dict[str, any] = {}
    
    def get_parameter(self, key: str, default: any = None) -> any:
        """Get a parameter value with a default if not found."""
        return self.parameters.get(key, default)

class AgentResponse(BaseModel):
    response: str
    success: bool
    updated_context: Dict[str, any] = {}
    suggestions: List[str] = []
    data: Optional[Dict[str, any]] = None

class BaseAgent(ABC):
    """Base class for all agents in the system.
    
    All agents should inherit from this class and implement the abstract methods.
    """
    
    @abstractmethod
    async def can_handle(self, intent: str) -> bool:
        """Determine if this agent can handle the given intent."""
        logger.debug(f"Checking if {self.__class__.__name__} can handle intent: {intent}")
        raise NotImplementedError(
            f"Agent {self.__class__.__name__} must implement can_handle()"
        )

    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process the given request and return a response."""
        logger.info(f"{self.__class__.__name__} processing request: {request.input}")
        raise NotImplementedError(
            f"Agent {self.__class__.__name__} must implement process()"
        )

    @abstractmethod
    async def get_name(self) -> str:
        """Get the name of this agent."""
        logger.debug(f"Getting name for {self.__class__.__name__}")
        raise NotImplementedError(
            f"Agent {self.__class__.__name__} must implement get_name()"
        )

    async def get_description(self) -> str:
        """Get a description of what this agent does."""
        logger.debug(f"Getting description for {self.__class__.__name__}")
        return f"Agent {self.get_name()} - No description provided"

    async def cleanup(self) -> None:
        """Perform any necessary cleanup when the agent is being shut down."""
        logger.info(f"Cleaning up {self.__class__.__name__}")
        return None