import streamlit as st
import time
from utils import write_message
from agent import generate_response

# Page Config
st.set_page_config(page_title="Medical RAG", page_icon=":hospital:")

# Create a sidebar for navigation between pages (without the upload page)
page = st.sidebar.selectbox("Navigate", ["Chat with Assistant"])

# Set up Session State for Chat Page
if page == "Chat with Assistant":
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi, I'm your Medical Research Regulatory Compliance Assistant! How can I help you?"},
        ]

    # Submit handler
    def handle_submit(message):
        """
        Handles the submit of chat messages and generates a response using Neo4j data.
        """
        # List of spinner messages
        spinner_texts = [
            'Finding relevant regulations...',
            'Reading through regulations...',
            'Analyzing...',
            'Almost done...'
        ]

        # Show progress spinner while processing
        with st.spinner('Taking a deep breath...'):
            for text in spinner_texts:
                st.spinner(text)
                time.sleep(1)

            # Call the agent and handle possible errors
            try:
                response = generate_response(message)
                write_message('assistant', response)
            except Exception as e:
                # Handle parsing errors gracefully
                st.error(f"An error occurred: {str(e)}")
                write_message('assistant', "Sorry, I encountered an error while processing the response.")

    # Display messages in the chat
    for message in st.session_state.messages:
        write_message(message['role'], message['content'], save=False)

    # Handle user input
    if question := st.chat_input("What is up?"):
        # Display user message in chat
        write_message('user', question)

        # Generate a response
        handle_submit(question)
