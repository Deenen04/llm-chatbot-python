import streamlit as st
import time
from utils import write_message
from agent import generate_response
from upload import upload_file_to_s3_and_neo4j  # Updated to S3 upload

# Page Config
st.set_page_config(page_title="Medical RAG", page_icon=":hospital:")

# Create a sidebar for navigation between chat and upload pages
page = st.sidebar.selectbox("Navigate", ["Chat with Assistant", "Upload Files"])

def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            # Upload file to S3 and process with Neo4j
            upload_file_to_s3_and_neo4j(uploaded_file)
        except Exception as e:
            st.error(f"File upload failed: {str(e)}")

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

# Upload page for uploading files to S3 and Neo4j
elif page == "Upload Files":
    st.title("Upload Medical Documents")
    uploaded_file = st.file_uploader("Upload a file for embedding and analysis", type=["pdf", "txt", "docx"])

    # Handle file upload and processing
    if uploaded_file:
        handle_file_upload(uploaded_file)