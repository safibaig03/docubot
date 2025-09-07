import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

class RetrievalAgent:
    def __init__(self):
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        client = chromadb.Client()
        self.collection = client.get_or_create_collection(
            name="document_collection",
            embedding_function=self.embedding_function
        )

    def clear_collection(self):
        client = chromadb.Client()
        client.delete_collection(name="document_collection")
        self.collection = client.get_or_create_collection(
            name="document_collection",
            embedding_function=self.embedding_function
        )

    def add_documents(self, final_chunks: List[Dict[str, Any]]):
        if not final_chunks:
            return

        self.collection.add(
            ids=[chunk['id'] for chunk in final_chunks],
            documents=[chunk['content'] for chunk in final_chunks],
            metadatas=[chunk['metadata'] for chunk in final_chunks]
        )

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["metadatas", "documents"]
        )
        
        retrieved_docs_content = results.get('documents', [[]])[0]
        retrieved_docs_metadata = results.get('metadatas', [[]])[0]
        
        sources = [
            {"content": content, "metadata": metadata}
            for content, metadata in zip(retrieved_docs_content, retrieved_docs_metadata)
        ]
        return sources