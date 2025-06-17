import getpass
import os
from txt_procc import chunked_documents

if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", task_type="RETRIEVAL_DOCUMENT")

# Creating the chunks
def create_embeddings_for_chunks(chunked_documents):
    """
    Create embeddings for chunked documents from multiple directories
    """
    embeddings_data = {}
    
    for location, chunks in chunked_documents.items():
        print(f"Creating embeddings for {location}...")
        
        # Extract text content from chunks
        chunk_texts = [chunk.page_content for chunk in chunks]
        
        # Create embeddings in batch (more efficient)
        chunk_embeddings = embeddings.embed_documents(chunk_texts)
        
        # Store embeddings with metadata
        embeddings_data[location] = {
            'chunks': chunks,
            'embeddings': chunk_embeddings,
            'texts': chunk_texts
        }
        
        print(f"Created {len(chunk_embeddings)} embeddings for {location}")
    
    return embeddings_data

# Using with your previous chunked documents
embeddings_data = create_embeddings_for_chunks(chunked_documents)

'''
Storing the embeddings in chromadb vector database
'''

import chromadb

# Initialize ChromaDB client
client = chromadb.Client()

def store_in_chromadb(embeddings_data):
    collections = {}
    
    for location, data in embeddings_data.items():
        # Create separate collection for each location
        collection_name = f"documents_{location}"
        collection = client.create_collection(name=collection_name)
        
        # Prepare data for ChromaDB
        ids = [f"{location}_{i}" for i in range(len(data['chunks']))]
        metadatas = []
        
        for i, chunk in enumerate(data['chunks']):
            metadata = {
                'source': chunk.metadata.get('source', ''),
                'location': location,
                'chunk_index': i
            }
            metadatas.append(metadata)
        
        # Add to collection
        collection.add(
            embeddings=data['embeddings'],
            documents=data['texts'],
            metadatas=metadatas,
            ids=ids
        )
        
        collections[location] = collection
        print(f"Stored {len(data['embeddings'])} embeddings in collection '{collection_name}'")
    
    return collections

# Store embeddings in ChromaDB
collections = store_in_chromadb(embeddings_data)

'''testing code'''

def list_collection_names(client):
    """
    Simply list all collection names
    """
    collections = client.list_collections()
    print("📁 Available Collections:")
    for collection in collections:
        print(f"  └── {collection.name}")

# Use it
list_collection_names(client)
