from typing import Any, Dict, Optional
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from ..models import (
    User,
    Conversation
)

class CosmosRepository:
    def __init__(self, connection_string: str, database_name: str):
        self.client = CosmosClient.from_connection_string(connection_string)
        self.database = self.client.get_database_client(database_name)
        self.user_container = self.database.get_container_client("users")
        self.conversation_container = self.database.get_container_client("conversations")

    async def save_user(self, user: User) -> None:
        """Save or update a user in Cosmos DB."""
        try:
            self.user_container.upsert_item(user.model_dump())
        except exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to save user: {e.message}")

    async def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID from Cosmos DB."""
        try:
            user_item = self.user_container.read_item(item=user_id, partition_key=user_id)
            return User(**user_item)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to retrieve user: {e.message}")

    async def save_conversation(self, conversation: Conversation) -> None:
        """Save or update a conversation in Cosmos DB."""
        try:
            self.conversation_container.upsert_item(conversation.model_dump())
        except exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to save conversation: {e.message}")

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by its ID from Cosmos DB."""
        try:
            conversation_item = self.conversation_container.read_item(item=conversation_id, partition_key=conversation_id)
            return Conversation(**conversation_item)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to retrieve conversation: {e.message}")

    async def update_conversation(self, conversation_id: str, updates: Dict[str, Any]) -> Optional[Conversation]:
        """Update a conversation by its ID with the provided updates."""
        try:
            conversation_item = self.conversation_container.read_item(item=conversation_id, partition_key=conversation_id)
            for key, value in updates.items():
                if key in conversation_item:
                    conversation_item[key] = value
            self.conversation_container.upsert_item(conversation_item)
            return Conversation(**conversation_item)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to update conversation: {e.message}")