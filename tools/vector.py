import numpy as np
import faiss
from llm import model  # Import the OpenAIEmbeddings model from llm.py
from graph import graph  # Import the Neo4jGraph connection from graph.py

# List of available documents
documents = [
    "Standard-operating-procedures-for-pharmaceuticals-good-distribution-and-storage-practices.pdf"
]

# Function to get embedding for a query text using llm.py's model
def get_embedding(text):
    return np.array(model.embed_query(text), dtype=np.float32)

def fetch_embeddings_from_neo4j(document_name):
    with graph._driver.session() as session:
        # Fetch only entity embeddings from the specified document
        entity_query = """
        MATCH (e:Entity)
        WHERE e.file_name = $document_name
        RETURN e.name AS id, e.embedding AS embedding
        """
        entity_results = list(session.run(entity_query, document_name=document_name))

    embeddings = []
    ids = []

    # Process entity embeddings only
    for record in entity_results:
        embeddings.append(np.array(record["embedding"], dtype=np.float32))
        ids.append(record["id"])

    return np.array(embeddings), ids

def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def query_faiss_index(query_embedding, index, ids, top_k=3):
    distances, indices = index.search(query_embedding, top_k)
    results = [(ids[i], distances[0][idx]) for idx, i in enumerate(indices[0])]
    return results

def get_entity_details_with_chunks(entity_name):
    with graph._driver.session() as session:
        query = """
        MATCH (e:Entity {name: $entity_name})-[:MENTIONS]-(chunk:Chunk)
        RETURN e.descriptions AS descriptions, 
               collect({
                   content: chunk.content, 
                   page_number: chunk.page_number, 
                   filename: chunk.file_name
               }) AS connected_chunk_details
        """
        result = session.run(query, entity_name=entity_name)
        return result.single()

def get_medic_docs(input_text):
    """
    Queries all available documents individually by retrieving only relevant chunks from each document.
    """
    responses = {}
    query_embedding = get_embedding(input_text).reshape(1, -1)

    for document in documents:
        embeddings, ids = fetch_embeddings_from_neo4j(document)
        if embeddings.size == 0:
            continue

        index = build_faiss_index(embeddings)
        results = query_faiss_index(query_embedding, index, ids, top_k=5)

        context = ""
        metadata = []

        for result in results:
            entity_name = result[0]
            distance = result[1]

            # Get details of the entity and its connected chunks
            entity_details = get_entity_details_with_chunks(entity_name)
            if entity_details:
                descriptions = entity_details['descriptions']
                connected_chunks = entity_details['connected_chunk_details']

                # Collect context and metadata
                context += f"\nEntity: {entity_name}\nDescription: {descriptions}\n"
                for chunk in connected_chunks:
                    context += f"Chunk Content: {chunk['content']}\n"
                    metadata.append({
                        "document_name": chunk['filename'],
                        "page_number": chunk['page_number'],
                        "distance": distance
                    })

        # Structure the response similarly to the example method
        enriched_result = {
            "context": context.strip(),
            "metadata": metadata,
            "chunks": results
        }
        responses[document] = enriched_result

    return responses

# # Example query
# results = get_medic_docs("what are the audit requirements?")
# for doc_name, result in results.items():
#     print(f"Document: {doc_name}\nContext:\n{result['context']}\nMetadata:\n{result['metadata']}\n")
