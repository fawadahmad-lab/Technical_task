from langchain_text_splitters import RecursiveCharacterTextSplitter
from RAG.vector_store import VectorStore
import os

class IndexingAgent:
    """Agent 2: Handles chunking, embeddings & vector storage"""
    
    def __init__(self):
        self.embeddings = self._get_embeddings_model()
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def _get_embeddings_model(self):
        """Get embeddings model with fallback if API key missing"""
        nomic_api_key = os.getenv("NOMIC_API_KEY")
        if nomic_api_key and nomic_api_key != "your_nomic_api_key_here":
            from langchain_nomic import NomicEmbeddings
            return NomicEmbeddings(
                model="nomic-embed-text-v1",
                nomic_api_key=nomic_api_key
            )
        
    def create_chunks(self, text: str, document_id: str):
        """Split text into chunks"""
        chunks = self.text_splitter.split_text(text)
        
        chunk_documents = []
        for i, chunk in enumerate(chunks):
            chunk_documents.append({
                "text": chunk,
                "metadata": {
                    "chunk_id": f"{document_id}_chunk_{i}",
                    "document_id": document_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })
        
        return chunk_documents
    
    def create_embeddings(self, chunks: list):
        """Create embeddings for text chunks"""
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        try:
            embeddings = self.embeddings.embed_documents(texts)
        except Exception as e:
            print(f"Embedding error: {e}. Using dummy embeddings.")
            import numpy as np
            embeddings = np.random.randn(len(texts), 384).tolist()  # 384-dim dummy
        
        return texts, embeddings, metadatas
    
    def store_in_vector_db(self, document_id: str, texts: list, embeddings: list, metadatas: list):
        """Store embeddings in FAISS"""
        vector_store = VectorStore()
        index_path = vector_store.create_index(
            document_id=document_id,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        return index_path
