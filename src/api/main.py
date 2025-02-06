from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .dependencies import get_orchestrator
from ..models.user import UserInput, UserResponse, Conversation
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="RoamMind",
    description="Travel planning assistant API leveraging Semantic Kernel",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/conversations/{conversation_id}/messages", response_model=UserResponse)
async def process_message(conversation_id: str, user_input: UserInput):
    """
    Process a user message via the Semantic Kernel orchestrator.
    Relies on orchestrator present in dependencies, which handles LLM calls,
    conversation state and integrates with the repository layer.
    """
    try:
        orchestrator = await get_orchestrator()
        response = await orchestrator.process_user_input(conversation_id, user_input.message)
        return UserResponse(
            response=response.response,
            success=response.success,
            data=response.data,
            suggestions=response.suggestions,
        )
    except Exception as e:
        logger.exception(f"Unexpected error processing message for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")

@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """
    Retrieve an existing conversation using the Semantic Kernel orchestrator.
    The orchestrator abstracts all repository interactions.
    """
    try:
        orchestrator = await get_orchestrator()
        conversation = await orchestrator.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        logger.exception(f"Unexpected error retrieving conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving conversation. Please try again later.")

@app.get("/health")
async def health_check():
    """
    Health check endpoint to ensure API and orchestrator dependencies are working.
    """
    return {"status": "healthy"}