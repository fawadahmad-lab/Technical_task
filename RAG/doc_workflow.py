import os
import sqlite3
from datetime import datetime
from agents.Ingestion_Agent import IngestionAgent
from agents.Indexing_Agent import IndexingAgent
from RAG.vector_store import VectorStore
def doc_workflow(document_id: str, filepath: str) -> dict:
    """Orchestrate document processing workflow"""
    
    import os
    file_ext = os.path.splitext(filepath)[1].lower()
    is_image = file_ext in ['.png', '.jpg', '.jpeg']
    
    print(f"Starting workflow for document: {document_id}, type: {'image' if is_image else 'pdf'}")
    
    try:
        # Agent 1: Ingestion
        ingestion_agent = IngestionAgent()
        raw_text = ingestion_agent.extract_text(filepath)
        clean_text = ingestion_agent.clean_text(raw_text)
        
        # Agent 2: Indexing
        indexing_agent = IndexingAgent()
        chunks = indexing_agent.create_chunks(clean_text, document_id)
        texts, embeddings, metadatas = indexing_agent.create_embeddings(chunks)
        
        # Add file type to metadata
        for metadata in metadatas:
            metadata['file_type'] = 'image' if is_image else 'pdf'
            metadata['original_filename'] = os.path.basename(filepath)
            metadata['is_image'] = is_image
        
        # Store in vector DB
        vector_store = VectorStore()
        index_path = vector_store.create_index(
            document_id=document_id,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        return {
            "chunks_count": len(chunks),
            "vector_store": index_path,
            "document_id": document_id,
            "file_type": "image" if is_image else "pdf"
        }
        
    except Exception as e:
        print(f"Error in workflow: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Document processing failed: {str(e)}")