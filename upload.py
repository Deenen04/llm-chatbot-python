"""
    This is for the function that will handle the upload of files to the Neo4j database for the purpose of querying these documents.

    Problem:
    - When we had to host the application, we realized that the python libraries that worked on our personal PCs when edited were not the same as those located on the server.
    - This meant our embedding function was rendered useless, as it couldn't function with the downloaded Neo4j vector library on the server. We were able to edit the one 
        on our PCs but couldn't edit the one on the server.
    - So our whole hypothesis fell at the point of hosting.

    We decided to tackle it as soon as possible; otherwise, we shall fail to create this thing as a hosted product. SO we came up with the following solution.
    Solution:
    - Use the original embedding model by the llm-chatbot-python repository by NEO4J.
    - Get Neo4J Database upload function from API docs.
    - Make a function to upload embedded documents (by the same function) to the NEO4J database.
    - All required variables must be declared with a description of where they should come from.
    That function is the upload function.

    Test:
    - Empty your Neo4j database.
    - Know the names of the documents you upload.
    Run the function taking the document directory as an input variable/parameter.
    - If that document appears in the empty Neo4J database, then the function works.
    Do it 3 times for each of the documents:
    - First time - one by one.
    - Second time in groups of 5.
    - Third time in groups of 50.

    Keep increasing the number of scalable groups while adjusting accordingly for the sake of knowing how to scale the system. Once we understand how to technically scale, then we can simply focus on marketing, as production will be done.
    
    Business:
    The goal is to have the blueprint of how to efficiently create usable software.

    Once we know exactly how, then we focus entirely on marketing the same product to different industries for as much as we want, as we shall be the only ones providing these services. 

    And when we have a client base in an industry, we start moving things to take over that industry; we strategically position ourselves to be at the source of information. Then what everybody in that industry hears is what we tell them.

    That way, we start to be paid the real monetary prices; there is no gold greater than hope. He who has struck hope has struck gold.
"""
import streamlit as st
import fitz
import os
import boto3
from docx import Document
from neo4j import GraphDatabase
from llm import model

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=st.secrets['AWS_ACCESS_KEY'],
    aws_secret_access_key=st.secrets['AWS_SECRET_KEY'],
    region_name=st.secrets['AWS_REGION']
)

# NEO4J Driver initialization
driver = GraphDatabase.driver(st.secrets["NEO4J_URI"], auth=("neo4j", st.secrets["NEO4J_PASSWORD"]))

# 1. File Upload and Save
def save_uploaded_file(uploaded_file):
    file_path = uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# 2. Text Extraction Functions
def extract_text_from_pdf(file_path):
    with fitz.open(file_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# 3. Determine File Type and Extract Text
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

# 4. Generate OpenAI Embeddings
def generate_embeddings(text):
    return model.embed_query(text)

# 5. Create and Upload to Neo4j with Chunk Handling
def upload_to_neo4j(file_name, chunks):
    with driver.session(database="neo4j") as session:
        for page_number, (chunk_text, doc_embedding) in enumerate(chunks, start=1):
            # Create the document node for each chunk
            query = """
            MERGE (d:Chunk {fileName: $file_name, text: $chunk_text, page_number: $page_number})
            SET d.embedding = $embedding
            """
            session.run(query, file_name=file_name, chunk_text=chunk_text, embedding=doc_embedding, page_number=page_number)
            
            # Create relationships with existing chunks
            existing_chunks = session.run("MATCH (d:Chunk) RETURN d.fileName AS fileName").data()
            for existing_chunk in existing_chunks:
                session.run("""
                    MATCH (d:Chunk {fileName: $new_file_name})
                    MATCH (e:Chunk {fileName: $existing_file_name})
                    MERGE (d)-[:RELATED_TO]->(e)
                    """, new_file_name=file_name, existing_file_name=existing_chunk['fileName'])

# 6. Upload File to S3
def upload_file_to_s3(file_path, file_name):
    try:
        s3_client.upload_file(file_path, st.secrets['S3_BUCKET_NAME'], file_name)
        st.success(f"File '{file_name}' uploaded to S3 successfully!")
    except Exception as e:
        st.error(f"Failed to upload file to S3: {str(e)}")

def upload_file_to_s3_and_neo4j(uploaded_file):
    # 1. Save the uploaded file locally
    file_path = save_uploaded_file(uploaded_file)
    
    # 2. Upload file to S3
    upload_file_to_s3(file_path, uploaded_file.name)
    
    # 3. Extract text based on file type
    document_text = extract_text(file_path)
    
    # 4. Chunk the document
    chunk_size = 1000  # Define your chunk size
    chunks = [(document_text[i:i + chunk_size], generate_embeddings(document_text[i:i + chunk_size]))
              for i in range(0, len(document_text), chunk_size)]
    
    # 5. Upload extracted text and embeddings to Neo4j
    upload_to_neo4j(uploaded_file.name, chunks)

    # 6. Confirm success
    st.success("File uploaded and embedded successfully!")