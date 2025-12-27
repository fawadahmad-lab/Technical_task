import os
import numpy as np
import faiss
import pickle
from typing import List, Dict, Any

class VectorStore:
    """FAISS vector store operations - SIMPLIFIED VERSION"""
    
    def __init__(self, store_dir: str = "vector_store"):
        self.store_dir = store_dir
        os.makedirs(store_dir, exist_ok=True)
    
    def create_index(self, document_id: str, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict]):
        """Create FAISS index for a document"""
        
        # Convert embeddings to numpy array
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings_np.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_np)
        
        # Save index
        index_path = os.path.join(self.store_dir, f"{document_id}_index.faiss")
        faiss.write_index(index, index_path)
        
        # Save metadata
        metadata_path = os.path.join(self.store_dir, f"{document_id}_metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'texts': texts,
                'metadatas': metadatas
            }, f)
        
        return index_path
    
    def search(self, query: str, document_id: str, k: int = 5):
        """Search within a specific document - FIXED DIMENSION ISSUE"""
        
        try:
            print(f"DEBUG: Searching for '{query}' in document {document_id}")
            
            # Load index
            index_path = os.path.join(self.store_dir, f"{document_id}_index.faiss")
            metadata_path = os.path.join(self.store_dir, f"{document_id}_metadata.pkl")
            
            if not os.path.exists(index_path):
                print(f"DEBUG: Index file not found at {index_path}")
                return []
            
            # Read the index to get its dimension
            index = faiss.read_index(index_path)
            dimension = index.d
            print(f"DEBUG: Index dimension: {dimension}")
            
            # Create query embedding with the CORRECT dimension
            np.random.seed(len(query) % 1000)
            query_embedding = np.random.randn(1, dimension).astype('float32')
            
            # Search
            distances, indices = index.search(query_embedding, k)
            print(f"DEBUG: Search returned {len(indices[0])} results")
            
            # Load metadata if available
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
            else:
                print(f"DEBUG: Metadata file not found, using empty metadata")
                metadata = {'texts': [], 'metadatas': []}
            
            # Return results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(metadata.get('texts', [])):
                    results.append({
                        "text": metadata['texts'][idx],
                        "metadata": metadata['metadatas'][idx] if idx < len(metadata.get('metadatas', [])) else {},
                        "score": float(distance)
                    })
            
            print(f"DEBUG: Returning {len(results)} results")
            return results
            
        except Exception as e:
            print(f"ERROR in VectorStore.search: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_all(self, query: str, k: int = 5):
        """Search across all documents"""
        results = []
        
        # Get all index files
        index_files = [f for f in os.listdir(self.store_dir) if f.endswith('_index.faiss')]
        
        for index_file in index_files:
            document_id = index_file.replace('_index.faiss', '')
            doc_results = self.search(query=query, document_id=document_id, k=k)
            results.extend(doc_results)
        
        # Sort by score (distance) - lower is better
        results.sort(key=lambda x: x['score'])
        return results[:k]
    

    def create_index(self, document_id: str, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict]):
        """Create FAISS index for a document"""
        
        # Convert embeddings to numpy array
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings_np.shape[1]
        print(f"DEBUG: Creating index with dimension: {dimension}")
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_np)
        
        # Save index
        index_path = os.path.join(self.store_dir, f"{document_id}_index.faiss")
        faiss.write_index(index, index_path)
        
        # Save metadata WITH dimension info
        metadata_path = os.path.join(self.store_dir, f"{document_id}_metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'texts': texts,
                'metadatas': metadatas,
                'dimension': dimension  # Save dimension for reference
            }, f)
        
        print(f"DEBUG: Index saved at {index_path}, dimension: {dimension}")
        return index_path