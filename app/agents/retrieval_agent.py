import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

# This agent is responsible for all interactions with the vector database.
# It handles embedding creation, storage, and semantic search.
class RetrievalAgent:
    def __init__(self):
        # Initialize the SentenceTransformer model that will be used to create embeddings.
        # This is passed to ChromaDB to ensure consistency between indexing and querying.
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        # Initialize the ChromaDB client.
        client = chromadb.Client()
        # Get or create a collection (like a table in a traditional DB)
        # This collection will use our specified model to embed documents automatically.
        self.collection = client.get_or_create_collection(
            name="document_collection",
            embedding_function=self.embedding_function
        )

    def clear_collection(self):
        # Clears all data from the vector store to start a fresh session.
        # The most robust way is to delete and immediately re-create the collection.
        client = chromadb.Client()
        client.delete_collection(name="document_collection")
        self.collection = client.get_or_create_collection(
            name="document_collection",
            embedding_function=self.embedding_function
        )

    def add_documents(self, final_chunks: List[Dict[str, Any]]):
        # Adds a batch of processed document chunks to the ChromaDB collection.
        if not final_chunks:
            return

        self.collection.add(
            ids=[chunk['id'] for chunk in final_chunks],
            documents=[chunk['content'] for chunk in final_chunks],
            metadatas=[chunk['metadata'] for chunk in final_chunks]
        )

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # Performs a semantic search on the vector database.
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["metadatas", "documents"]
        )
        
        # Safely extract the content and metadata from the search results.
        retrieved_docs_content = results.get('documents', [[]])[0]
        retrieved_docs_metadata = results.get('metadatas', [[]])[0]
        
        # Format the results into a clean list of dictionaries for the CoordinatorAgent.
        sources = [
            {"content": content, "metadata": metadata}
            for content, metadata in zip(retrieved_docs_content, retrieved_docs_metadata)
        ]
        return sources