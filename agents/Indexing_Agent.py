from langchain_text_splitters import RecursiveCharacterTextSplitter
from RAG.vector_store import VectorStore
import os
import numpy as np

class IndexingAgent:
    """
    Agent 2: Text Chunking, Embedding & Vector Indexing
    
    Purpose:
        Transforms raw extracted text into searchable vector representations
        and stores them in a vector database for efficient semantic retrieval.
        This is the critical middle layer of the RAG pipeline that bridges
        raw text and intelligent question answering.
    
    What it does:
        1. Text Chunking:
           - Splits long documents into smaller, semantically coherent chunks
           - Uses recursive splitting to preserve sentence and paragraph boundaries
           - Creates overlapping chunks to maintain context across splits
           - Adds metadata to each chunk for traceability
        
        2. Embedding Generation:
           - Converts text chunks into 384-dimensional vector embeddings
           - Uses Nomic AI's "nomic-embed-text-v1" model for semantic encoding
           - Captures semantic meaning beyond keyword matching
           - Falls back to random embeddings if API unavailable
        
        3. Vector Storage:
           - Stores embeddings in FAISS (Facebook AI Similarity Search)
           - Maintains association between vectors and source metadata
           - Enables fast similarity search at query time
           - Returns index path for future retrieval operations
    
    Key Features:
        - Intelligent text splitting with configurable parameters
        - Semantic embeddings capture meaning and context
        - Metadata preservation for source attribution
        - Graceful degradation with dummy embeddings
        - Efficient vector storage using FAISS
        - Document-level indexing with chunk tracking
    
    Technical Details:
        - Chunk Size: 1000 characters (optimal for context preservation)
        - Chunk Overlap: 200 characters (20% overlap prevents context loss)
        - Embedding Dimensions: 384 (Nomic model standard)
        - Vector Store: FAISS (CPU-based similarity search)
    
    Pipeline Flow:
        Raw Text → Chunks → Embeddings → Vector DB → Searchable Index
    
    Usage Example:
        agent = IndexingAgent()
        chunks = agent.create_chunks(text, "doc_123")
        texts, embeddings, metadata = agent.create_embeddings(chunks)
        index_path = agent.store_in_vector_db("doc_123", texts, embeddings, metadata)
    
    Dependencies:
        - langchain_text_splitters: For intelligent text chunking
        - langchain_nomic: For embedding generation (requires API key)
        - numpy: For dummy embeddings fallback
        - RAG.vector_store: Custom FAISS wrapper
    
    Environment Variables:
        - NOMIC_API_KEY: Required for Nomic embeddings (optional, has fallback)
    """
    
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """
        Initialize the indexing agent with embedding model and text splitter.
        
        Args:
            chunk_size: Maximum characters per chunk (default: 1000)
            chunk_overlap: Overlapping characters between chunks (default: 200)
        """
        self.embeddings = self._init_embeddings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
    
    def _init_embeddings(self):
        """Initialize embeddings model with API key validation"""
        key = os.getenv("NOMIC_API_KEY")
        if key and key != "your_nomic_api_key_here":
            try:
                from langchain_nomic import NomicEmbeddings
                return NomicEmbeddings(
                    model="nomic-embed-text-v1",
                    nomic_api_key=key
                )
            except Exception as e:
                print(f"Failed to load Nomic embeddings: {e}")
        return None
    
    def create_chunks(self, text: str, document_id: str) -> list:
        """
        Split text into overlapping chunks with metadata.
        
        Args:
            text: Raw text to chunk
            document_id: Unique identifier for the source document
            
        Returns:
            List of dictionaries with 'text' and 'metadata' keys
        """
        chunks = self.splitter.split_text(text)
        return [{
            "text": chunk,
            "metadata": {
                "chunk_id": f"{document_id}_chunk_{i}",
                "document_id": document_id,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
        } for i, chunk in enumerate(chunks)]
    
    def create_embeddings(self, chunks: list) -> tuple:
        """
        Generate vector embeddings for text chunks.
        
        Args:
            chunks: List of chunk dictionaries from create_chunks()
            
        Returns:
            Tuple of (texts, embeddings, metadatas)
            - texts: List of chunk text strings
            - embeddings: List of 384-dim vectors
            - metadatas: List of metadata dictionaries
        """
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        
        # Try real embeddings, fallback to dummy
        try:
            embeddings = (self.embeddings.embed_documents(texts) 
                         if self.embeddings else None)
        except Exception as e:
            print(f"Embedding error: {e}. Using dummy embeddings.")
            embeddings = None
        
        if embeddings is None:
            embeddings = np.random.randn(len(texts), 384).tolist()
        
        return texts, embeddings, metadatas
    
    def store_in_vector_db(self, document_id: str, texts: list, 
                          embeddings: list, metadatas: list) -> str:
        """
        Store embeddings in FAISS vector database.
        
        Args:
            document_id: Unique identifier for the document
            texts: List of text chunks
            embeddings: List of vector embeddings
            metadatas: List of metadata dictionaries
            
        Returns:
            Path to the stored FAISS index file
        """
        vector_store = VectorStore()
        return vector_store.create_index(
            document_id=document_id,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )