import streamlit as st
from llm import llm, embeddings
from graph import graph

# Create the Neo4jVector
from langchain_community.vectorstores.neo4j_vector import Neo4jVector

neo4jvector = Neo4jVector.from_existing_index(
    embeddings,                              # (1)
    graph=graph,                             # (2)
    index_name= "vector",                 # (3) After relationships have been created
    node_label="Chunk",                      # (4)
    text_node_property="text",               # (5)
    embedding_node_property="embedding", # (6)
    retrieval_query="""
    MATCH (node:Chunk)
    WHERE node.fileName IS NOT NULL
    RETURN
        node.text AS text,
        score,
        {
            document_name: node.fileName,
            page_number: COALESCE(node.page_number, 'N/A')
        } AS metadata
    """
)

# Create the retriever
retriever = neo4jvector.as_retriever(search_type="similarity", search_kwargs={"k": 7})  # Adjust "k" to retrieve more chunks

# Create the prompt
from langchain_core.prompts import ChatPromptTemplate

instructions = (
    "Use the given context to answer the question. "
    "If you don't know the answer, say you don't know. "
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

# Create the chain 
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

question_answer_chain = create_stuff_documents_chain(llm, prompt)

# List of available documents
documents = [
    "Data-Integrity-and-Compliance-With-Current-Good-Manufacturing-Practice-Guidance-for-Industry.pdf",
    "annex11_01-2011_en_0.pdf",
    "PI 041-1 Guidance on Data Integrity.pdf",
    "MHRA_GxP_data_integrity_guide_March_edited_Final.pdf",
    "21 CFR Part 11 (up to date as of 8-06-2024).pdf"
]

def get_medic_docs(input):
    """
    Queries all available documents individually by retrieving only relevant chunks from each document.
    """
    responses = {}
    for document in documents:
        retrieval_query = f"""
        MATCH (node:Chunk) 
        WHERE node.fileName = '{document}' 
        RETURN node.text AS text, score, {{ document_name: node.fileName, page_number: COALESCE(node.page_number, 'N/A') }} AS metadata
        """
        neo4jvector.retrieval_query = retrieval_query
        result = retriever.get_relevant_documents(input)

        # Log the retrieved chunks for debugging
        if isinstance(result, list):
            context = " ".join([doc.page_content for doc in result])
            metadata = [doc.metadata for doc in result]
            enriched_result = {"context": context, "metadata": metadata, "chunks": result}
            responses[document] = enriched_result
    return responses