import streamlit as st
import time
from utils import write_message
from agent import generate_response

# Page Config
st.set_page_config("Ebert", page_icon=":movie_camera:")

# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm the GraphAcademy Chatbot!  How can I help you?"},
    ]

# Submit handler
# Submit handler
def handle_submit(message):
    """
    Submit handler:

    You will modify this method to talk with an LLM and provide
    context using data from Neo4j.
    """
    # List of spinner messages
    spinner_texts = [
        'Finding relevant regulations...',
        'Reading through regulations...',
        'Analyzing...',
        'Almost done...'
    ]
    
    # Handle the response
    with st.spinner('Taking a deep breath...'):
        for text in spinner_texts:
            st.spinner(text)
            time.sleep(1)
        
        # Call the agent and handle possible parsing issues
        try:
            response = generate_response(message)
            write_message('assistant', response)
        except Exception as e:
            # Handle output parsing errors gracefully
            st.error(f"An error occurred, but the response was processed: {str(e)}")
            # Provide fallback output if necessary
            write_message('assistant', "Here is the response, despite the error encountered.")

# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if question := st.chat_input("What is up?"):
    # Display user message in chat message container
    write_message('user', question)

    # Generate a response
    handle_submit(question)
