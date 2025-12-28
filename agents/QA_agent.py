from langchain_groq import ChatGroq
from RAG.vector_store import VectorStore

class QAAgent:
    """
    Agent 3: Semantic Retrieval & Answer Generation
    
    Purpose:
        The final stage of the RAG pipeline that retrieves relevant context
        from the vector database and generates accurate, context-aware answers
        using a Large Language Model.
    
    What it does:
        - Converts user questions into vector embeddings
        - Performs semantic similarity search in the vector database
        - Retrieves the top-k most relevant document chunks
        - Distinguishes between image-based and text-based content
        - Generates natural language answers using Groq's LLaMA model
        - Provides source attribution and context references
        - Handles both single-document and multi-document queries
    
    Key Features:
        - Semantic search across entire document collection
        - Special handling for image-related queries
        - Context-aware answer generation using LLM
        - Source tracking and attribution
        - Fallback responses when LLM is unavailable
        - Multi-document retrieval support
    
    Configuration:
        - Default model: llama-3.3-70b-versatile (Groq)
        - Default temperature: 0.1 (more factual, less creative)
        - Default k: 5 (retrieves top 5 relevant chunks)
    
    Output:
        Dictionary containing:
        - answer: Natural language response to the query
        - sources: Top relevant chunks with metadata
        - contains_images: Boolean flag for image content
    """
    
    def __init__(self, model="llama-3.3-70b-versatile", temperature=0.1):
        self.llm = self._init_llm(model, temperature)
        self.vector_store = VectorStore()
    
    def _init_llm(self, model: str, temperature: float):
        """Initialize LLM with error handling"""
        try:
            return ChatGroq(model=model, temperature=temperature)
        except Exception as e:
            print(f"LLM initialization failed: {e}")
            return None
    
    def answer_question(self, question: str, document_id: str = None, k: int = 5) -> dict:
        """Answer question with retrieved context"""
        results = (self.vector_store.search(question, document_id, k) if document_id 
                  else self.vector_store.search_all(question, k))
        
        if not results:
            return {"answer": "No relevant information found.", "sources": [], 
                   "contains_images": False}
        
        image_results = [r for r in results if r.get('metadata', {}).get('file_type') == 'image']
        is_image_query = "image" in question.lower() and image_results
        
        answer = (self._answer_image(results, question) if is_image_query 
                 else self._answer_general(results, question))
        
        return {
            "answer": answer,
            "sources": results[:3],
            "contains_images": bool(image_results)
        }
    
    def _answer_image(self, results: list, question: str) -> str:
        """Generate answer about images"""
        context = "\n\n".join([
            f"From {r['metadata'].get('original_filename', 'an image')}: {r['text'][:300]}"
            for r in results if r.get('metadata', {}).get('file_type') == 'image'
        ])
        
        if not context:
            return "No image information found."
        
        if self.llm:
            prompt = f"Based on these image summaries, answer: {question}\n\n{context}\n\nAnswer:"
            return self.llm.invoke(prompt).content
        return f"The images show: {context[:500]}..."
    
    def _answer_general(self, results: list, question: str) -> str:
        """Generate general answer"""
        context = "\n".join([r["text"] for r in results[:3]])
        
        if self.llm:
            prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer based on context:"
            return self.llm.invoke(prompt).content
        return f"Based on documents: {context[:500]}..."