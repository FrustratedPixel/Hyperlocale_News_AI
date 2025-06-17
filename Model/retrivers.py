from Embedding import embeddings, collections, embeddings_data

def create_retrievers_from_chromadb(collections, embeddings, k=12):
    """
    Create retrievers directly from existing ChromaDB collections
    No double-wrapping needed!
    """
    retrievers = {}
    
    for locality, collection in collections.items():
        
        def create_retriever_function(coll, emb_func):
            """Create a retriever function for this specific collection"""
            
            def retrieve(query: str, k: int = k):
                # Convert query to embedding
                query_embedding = emb_func.embed_query(query)
                
                # Query the ChromaDB collection directly
                results = coll.query(
                    query_embeddings=[query_embedding],
                    n_results=k,
                    include=['documents', 'metadatas']
                )
                
                # Convert results to Langchain Document format
                from langchain.schema import Document
                documents = []
                
                for i in range(len(results['documents'][0])):
                    doc = Document(
                        page_content=results['documents'][0][i],
                        metadata=results['metadatas'][0][i]
                    )
                    documents.append(doc)
                
                return documents
            
            return retrieve
        
        # Create retriever function for this locality
        retrievers[locality] = create_retriever_function(collection, embeddings)
        print(f"Created retriever for {locality} with k={k}")
    
    return retrievers

# Create retrievers from your existing collections
retrievers = create_retrievers_from_chromadb(collections, embeddings, k=12)
