import streamlit as st

# Create the LLM
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sentence_transformers import SentenceTransformer

llm = ChatOpenAI(
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    model=st.secrets["OPENAI_MODEL"],
)

# Create the OpenAI Embedding model
model = OpenAIEmbeddings(
    openai_api_key=st.secrets["OPENAI_API_KEY"]
)

# # Replace the OpenAI Embeddings with sentence-transformers model
# model = SentenceTransformer('sentence-transformers/msmarco-MiniLM-L-12-v3')

# # Function to create embeddings
# def create_embedding(content):
#     return embeddings.embed_query(content)

# Example usage with sentence-transformers
# content = "This is an example sentence."
# content_embedding = model.encode(content)

# # Example usage with OpenAI
# content = "This is an example sentence."
# content_embedding = create_embedding(content)
