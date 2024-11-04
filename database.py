import streamlit as st
from supabase import create_client, Client
from datetime import datetime

#Set up Client
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
supabase: Client = create_client(url, key)


# ------ CRUD OPERATIONS ------ #

# ---USER TABLE---#

# Create User
def create_user(username: str) -> str:
    """
        username must be unique as it is the identifier of which user had what conversations.
        Error response if the username already exists:
        Error creating user: {
            'code': '23505', 
            'details': 'Key (username)=(Cherry) already exists.',
            'hint': None, 
            'message': 'duplicate key value violates unique constraint "unique_username"'
        }

    """
    try:
         # Check if the username already exists
        existing_user = supabase.table("User").select("id").eq("username", username).execute()
        if existing_user.data:
            # If user exists, return the existing user_id
            user_id = existing_user.data[0]['id']
            print(f"User already exists. Returning existing user_id: {user_id}")
            return user_id
        
        # If user does not exist, create a new user
        created_at = datetime.now().isoformat()
        response = supabase.table("User").insert({
            "username": username,
            "created_at": created_at
        }).execute()
        return response.data[0]['id']
    
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user(username: str):
    """
        response = {
            'id': '1b5c9f47-9f8d-41fb-a2c2-f372437e7f84',
            'created_at': '2024-10-28T21:49:19.61842+00:00',
            'username': 'Ritah'
        }
    """
    try:
        response = supabase.table("User").select("*").eq("username", username).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error retrieving user by username: {e}")
        return None

def update_user(user_id: str, username: str):
    try:
        response = supabase.table("User").update({
            "username": username
        }).eq("id", user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating user: {e}")
        return None

def delete_user(user_id: str):
    try:
        response = supabase.table("User").delete().eq("id", user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error deleting user: {e}")
        return None

user_id = create_user("Cherry")
response = get_user("Cherry")
user_id = response['id']
print(user_id)
# print(update_user(user_id, "Mary"))
# print(get_user(user_id))

# --- CHAT TABLE ---#
def create_chat(user_id: str) -> str:
    try:
        created_at = datetime.now().isoformat()
        response = supabase.table("Chat").insert({
            "user_id": user_id,
            "created_at": created_at
        }).execute()
        return response.data[0]['id']
    except Exception as e:
        print(f"Error creating chat: {e}")
        return None

def get_chat(chat_id: str):
    try:
        response = supabase.table("Chat").select("*").eq("id", chat_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error retrieving chat: {e}")
        return None

def update_chat(chat_id: str, new_created_at: str):
    try:
        response = supabase.table("Chat").update({
            "created_at": new_created_at
        }).eq("id", chat_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating chat: {e}")
        return None

def delete_chat(chat_id: str):
    try:
        response = supabase.table("Chat").delete().eq("id", chat_id).execute()
        return response.data
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return None

# --- MESSAGE TABLE --- #
def create_message(chat_id: str, sender: str, content: str) -> str:
    try:
        created_at = datetime.now().isoformat()
        response = supabase.table("Message").insert({
            "chat_id": chat_id,
            "sender": sender,
            "content": content,
            "created_at": created_at
        }).execute()
        return response.data[0]['id']
    except Exception as e:
        print(f"Error creating message: {e}")
        return None

def get_message(message_id: str):
    try:
        response = supabase.table("Message").select("*").eq("id", message_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error retrieving message: {e}")
        return None

def update_message(message_id: str, content: str):
    try:
        response = supabase.table("Message").update({
            "content": content
        }).eq("id", message_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating message: {e}")
        return None

def delete_message(message_id: str):
    try:
        response = supabase.table("Message").delete().eq("id", message_id).execute()
        return response.data
    except Exception as e:
        print(f"Error deleting message: {e}")
        return None

# --- VKGResponse Table --- #
def create_vkg_response(content: str, message_id: str) -> str:
    try:
        created_at = datetime.now().isoformat()
        response = supabase.table("VKGResponse").insert({
            "content": content,
            "message_id": message_id,
            "created_at": created_at
        }).execute()
        return response.data[0]['id']
    except Exception as e:
        print(f"Error creating VKGResponse: {e}")
        return None

def get_vkg_response(vkg_response_id: str):
    try:
        response = supabase.table("VKGResponse").select("*").eq("id", vkg_response_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error retrieving VKGResponse: {e}")
        return None

def update_vkg_response(vkg_response_id: str, content: str):
    try:
        response = supabase.table("VKGResponse").update({
            "content": content
        }).eq("id", vkg_response_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating VKGResponse: {e}")
        return None

def delete_vkg_response(vkg_response_id: str):
    try:
        response = supabase.table("VKGResponse").delete().eq("id", vkg_response_id).execute()
        return response.data
    except Exception as e:
        print(f"Error deleting VKGResponse: {e}")
        return None


def get_messages_by_chat(chat_id: str):
    """
    Retrieves all messages associated with a given chat_id, ordered by the time they were created.
    :param chat_id: The ID of the chat to retrieve messages for.
    :return: A list of message records if found, otherwise an empty list.
    """
    try:
        response = supabase.table("Message").select("*").eq("chat_id", chat_id).order("created_at", desc=False).execute()
        print("Request sent to Supabase")
        return response.data if response.data else []
    except Exception as e:
        print(f"Error retrieving messages for chat_id {chat_id}: {e}")
        return []

def get_chats_by_user(user_id: str):
    try:
        response = supabase.table("Chat").select("id").eq("user_id", user_id).execute()
        return [chat["id"] for chat in response.data] if response.data else []
    except Exception as e:
        print(f"Error retrieving chats for user: {e}")
        return None








# def create_user(username: str) -> str:
#     """
#         Function to create the user, if user does not exist. 
#         Takes username and returns user_id as created by Supabase.
#     """
#     created_at = datetime.now().isoformat()

#     # Check if user already exists by username
#     existing_user = supabase.table("User").select("*").eq("username", username).execute()
    
#     if not existing_user.data:
#         # Create new user if not exists
#         response = supabase.table("User").insert({
#             "username": username,
#             "created_at": created_at
#         }).execute()
#         user_id = response.data[0]['id']
#         print("New user created.")
#     else:
#         user_id = existing_user.data[0]['id']
#         print("User already exists.")

#     return user_id

# def read_user(username: str) -> str:


# #Start New Chat

# def start_new_chat(user_id: str) -> str:
#     created_at = datetime.now().isoformat()

#     # Create a new chat entry
#     response = supabase.table("Chat").insert({
#         "user_id": user_id,
#         "created_at": created_at,
#     }).execute()
    
#     chat_id = response.data[0]['id']
#     print("New chat session started.")
#     return chat_id

# #Add message to chat
# def add_message(chat_id: str, sender: str, content: str):
#     created_at = datetime.now().isoformat()

#     # Insert the message into the Message table
#     supabase.table("Message").insert({
#         "created_at": created_at,
#         "chat_id": chat_id,
#         "sender": sender,
#         "content": content,    
#     }).execute()

#     print("Message added to chat.")

# #List Recent Chats
# def list_recent_chats(user_id: str, limit: int = 10):
#     # Fetch recent chats for the user
#     response = supabase.table("Chat").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
#     recent_chats = response.data

#     print("Recent chats retrieved.")
#     return recent_chats

# #Load Chat Messages
# def load_chat_messages(chat_id: str):
#     # Fetch messages for a chat
#     response = supabase.table("Message").select("*").eq("chat_id", chat_id).order("created_at").execute()
#     messages = response.data

#     print("Chat messages loaded.")
#     return messages

# user_id = create_user("benjamin")
# chat_id = "992b39bb-0d9c-4c68-a5a8-6d1d1de3dcf2"
# print(chat_id)

# sender = "USER"
# content = "Hello, I would liek to know how the medical research on patients for new drugs will be verified?"

# #add_message(chat_id=chat_id, sender=sender, content=content)
# print(list_recent_chats(user_id, 10))
# print(load_chat_messages(chat_id))
