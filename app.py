from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

app = FastAPI()

# Import CRUD functions from database.py
from database import create_user, get_user, create_chat, get_chat, create_message, get_messages_by_chat, get_chats_by_user
# Pydantic models for request and response data validation
class UserRequest(BaseModel):
    username: str

class MessageRequest(BaseModel):
    chat_id: str
    sender: str
    content: str

class ChatRequest(BaseModel):
    user_id: str

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    sender: str
    content: str
    created_at: datetime

# 1. User sign-up/login endpoint
@app.post("/signup")
async def signup(user: UserRequest):
    """
    HTTP Request Javascript:
        async function signup(username) {
            const response = await fetch(`${api_url}/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username }),
            });

            if (response.ok) {
                const userId = await response.json();
                console.log('User ID:', userId);
                return userId;
            } else {
                throw new Error('Signup failed: ' + response.statusText);
            }
        }
    
    Expected Response:
        Success: 200 OK with { "user_id": "string" }
        Error: 500 Internal Server Error with { "detail": "Unable to create or retrieve user." }

    """
    user_id = create_user(user.username)
    if user_id:
        return user_id
    raise HTTPException(status_code=500, detail="Unable to create or retrieve user.")

# 2. Create chat endpoint
@app.post("/chats/")
async def create_new_chat(chat_request: ChatRequest):
    """
    HTTP Request Javascript: 
        async function createChat(userId) {
            const response = await fetch(`${api_url}/chats/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId }),
            });

            if (response.ok) {
                const chatId = await response.json();
                console.log('Chat ID:', chatId);
                return chatId;
            } else {
                throw new Error('Chat creation failed: ' + response.statusText);
            }
        }
    Expected Response:
        Success: 200 OK with { "chat_id": "string" }
        Error: 500 Internal Server Error with { "detail": "Unable to create chat." }

    """
    chat_id = create_chat(chat_request.user_id)
    if chat_id:
        return chat_id
    raise HTTPException(status_code=500, detail="Unable to create chat.")

# 3. Create message within a chat
@app.post("/messages/")
async def create_message_endpoint(message_request: MessageRequest):
    """
    HTTP Request Javascript: 
        async function createMessage(chatId, sender, content) {
            const response = await fetch(`${api_url}/messages/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ chat_id: chatId, sender, content }),
            });

            if (response.ok) {
                const messageId = await response.json();
                console.log('Message ID:', messageId);
                return messageId;
            } else {
                throw new Error('Message creation failed: ' + response.statusText);
            }
        }
    Expected Response:
        Success: 200 OK with { "message_id": "string" }
        Error: 500 Internal Server Error with { "detail": "Unable to create message." }
    """
    message_id = create_message(
        chat_id=message_request.chat_id,
        sender=message_request.sender,
        content=message_request.content
    )
    if message_id:
        return message_id
    raise HTTPException(status_code=500, detail="Unable to create message.")

# 4. Retrieve all messages for a given chat
@app.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(chat_id: UUID):
    """
    HTTP Request Javascript:
        async function getChatMessages(chatId) {
            const response = await fetch(`${api_url}/chats/${chatId}/messages`);

            if (response.ok) {
                const messages = await response.json();
                console.log('Messages:', messages);
                return messages;
            } else {
                throw new Error('Failed to retrieve messages: ' + response.statusText);
            }
        }

    Expected Response:
        Success: 200 OK with { "messages": [{ "id": "string", "chat_id": "string", "sender": "string", "content": "string", "created_at": "string" }, ...] }
        Error: 404 Not Found with { "detail": "Messages not found for this chat." }

    """
    messages = get_messages_by_chat(chat_id)
    if messages is not None:
        return messages
    raise HTTPException(status_code=404, detail="Messages not found for this chat.")

# 5. Retreive all chats by user
@app.get("/chats/{user_id}")
async def get_chats(user_id: str):
    """
    HTTP Request Javascript:
        async function getUserChats(userId) {
            const response = await fetch(`${api_url}/chats/${userId}`);

            if (response.ok) {
                const chatIds = await response.json();
                console.log('Chat IDs:', chatIds);
                return chatIds;
            } else {
                throw new Error('Failed to retrieve chats: ' + response.statusText);
            }
        }
    Expected Response:
        Success: 200 OK with { "chat_ids": ["string", "string", ...] }
        Error: 500 Internal Server Error with { "detail": "Error retrieving chats" }
    """
    chats = get_chats_by_user(user_id)
    if chats is None:
        raise HTTPException(status_code=500, detail="Error retrieving chats")
    return {"chat_ids": chats}