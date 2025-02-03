from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .dependencies import get_orchestrator
from ..models.user import UserInput, UserResponse, Conversation
from typing import List
from ..utils.logger import *
from ..exceptions import RestaurantNotFoundError, FlightNotFoundError, ExcursionNotFoundError, HotelNotFoundError

logger = setup_logger(__name__)

app = FastAPI(
    title="RoamMind",
    description="Travel planning assistant API",
    version="1.0.0",
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
    try:
        orchestrator = get_orchestrator()
        response = await orchestrator.process_user_input(conversation_id, user_input.message)
        return UserResponse(
            response=response.response,
            success=response.success,
            data=response.data,
            suggestions=response.suggestions
        )
    except ValidationError as e:
        logger.error(f"Validation error: {e}. User Input: {user_input.message}")
        raise HTTPException(status_code=422, detail="Invalid input. Please check your request and try again.")
    except (RestaurantNotFoundError, FlightNotFoundError, ExcursionNotFoundError, HotelNotFoundError) as e:
        logger.error(f"API error or resource not found: {e}. User Input: {user_input.message}")
        raise HTTPException(status_code=500, detail="There was a problem processing your request. Please try again later.")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}. User Input: {user_input.message}")
        raise HTTPException(status_code=500, detail="Sorry, an unexpected error occurred. Please try again later.")


@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    try:
        orchestrator = get_orchestrator()
        conversation = await orchestrator.get_conversation(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail="Invalid input. Please check your request and try again.")
    except (RestaurantNotFoundError, FlightNotFoundError, ExcursionNotFoundError, HotelNotFoundError) as e:
        logger.error(f"Resource not found: {e}")
        raise HTTPException(status_code=404, detail="Resource not found")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving conversation. Please try again later.")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}