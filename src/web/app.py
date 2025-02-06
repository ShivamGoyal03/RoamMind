import streamlit as st
import requests
from typing import Dict, List, Any, Optional
import json
import uuid
from pydantic import BaseModel, Field

class TravelAIApp:
    def __init__(self):
        self.API_URL = "http://localhost:8000"
        self.setup_session_state()

    def setup_session_state(self):
        if "conversation_id" not in st.session_state:
            st.session_state.conversation_id = str(uuid.uuid4())
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def send_message(self, message: str) -> Dict:
        try:
            response = requests.post(
                f"{self.API_URL}/conversations/{st.session_state.conversation_id}/messages",
                json={"message": message},
            )
            return response.json()
        except Exception as e:
            st.error(f"Error sending message: {str(e)}")
            return {"error": str(e)}

    def display_travel_details(self, data: Dict):
        if "flights" in data:
            with st.expander("Flight Details"):
                st.table(data["flights"])
        if "hotels" in data:
            with st.expander("Hotel Details"):
                st.table(data["hotels"])
        if "restaurants" in data:
            with st.expander("Restaurant Details"):
                st.table(data["restaurants"])

    def run(self):
        st.title("Travel AI Assistant")
        
        # Simple input interface
        user_message = st.text_input("Enter your travel request:")
        
        if st.button("Send"):
            if user_message:
                response = self.send_message(user_message)
                st.write("Response:")
                st.json(response)
            else:
                st.warning("Please enter a message.")

class UserInput(BaseModel):
    message: str

class UserResponse(BaseModel):
    response: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

if __name__ == "__main__":
    app = TravelAIApp()
    app.run()