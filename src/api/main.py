from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from chainlit.server import app as chainlit_app
from ..models.user import UserInput, UserResponse, Conversation
from ..utils.logger import setup_logger
from ..core.orchestrator import Orchestrator

logger = setup_logger(__name__)

app = FastAPI(
    title="RoamMind",
    description="Travel planning assistant API leveraging Semantic Kernel",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Mount Chainlit app
app.mount("/", chainlit_app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize single orchestrator instance for the app
orchestrator = Orchestrator()

@app.post("/conversations/{conversation_id}/messages")
async def process_message(
    conversation_id: str,
    request: Request,
    user_input: UserInput
):
    """Process user messages in a conversation."""
    try:
        response = await orchestrator.process_user_input(
            conversation_id=conversation_id,
            message=user_input.message
        )
        return UserResponse(
            response=response["response"],
            success=True,
            data=response.get("data"),
            suggestions=response.get("suggestions", [])
        )
    except Exception as e:
        logger.exception(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Retrieve an existing conversation from session storage."""
    try:
        conversation = await orchestrator.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        logger.exception(f"Error retrieving conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving conversation")

@app.delete("/conversations/{conversation_id}")
async def end_conversation(conversation_id: str):
    """End a conversation and clean up its session data."""
    try:
        orchestrator.cleanup_session(conversation_id)
        return {"status": "success", "message": "Conversation ended"}
    except Exception as e:
        logger.exception(f"Error ending conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Error ending conversation")

@app.get("/health")
async def health_check():
    """Health check endpoint to ensure API is working."""
    return {"status": "healthy"}