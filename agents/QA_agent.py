from langchain_groq import ChatGroq
from RAG.vector_store import VectorStore

class QAAgent:
    """Agent 3: Retrieves context & generates answers"""
    
    def __init__(self):
        self.llm = self._get_llm()
    
    def _get_llm(self):
        """Get LLM for answers"""
        try:
            return ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.1
            )
        except:
            return None
    
    def answer_question(self, question: str, document_id: str = None):
        """Answer question with context about images"""
        
        # Get vector store results
        vector_store = VectorStore()
        
        if document_id:
            results = vector_store.search(query=question, document_id=document_id, k=5)
        else:
            results = vector_store.search_all(query=question, k=5)
        
        if not results:
            return {"answer": "No relevant information found.", "sources": []}
        
        # Check if any results are from images
        image_results = [r for r in results if r.get('metadata', {}).get('file_type') == 'image']
        
        if image_results and "image" in question.lower():
            # Special handling for image questions
            answer = self._answer_about_image(results, question)
        else:
            # Regular answer
            context = "\n".join([r["text"] for r in results[:3]])
            answer = self._generate_answer(context, question)
        
        return {
            "answer": answer,
            "sources": results[:3],
            "contains_images": len(image_results) > 0
        }
    
    def _answer_about_image(self, results, question):
        """Generate answer specifically about images"""
        image_context = []
        for result in results:
            if result.get('metadata', {}).get('file_type') == 'image':
                filename = result['metadata'].get('original_filename', 'an image')
                image_context.append(f"From {filename}: {result['text'][:300]}")
        
        if not image_context:
            return "No image information found."
        
        context = "\n\n".join(image_context)
        
        if self.llm:
            prompt = f"""Based on these image summaries, answer: {question}
            
            Image Summaries:
            {context}
            
            Answer specifically about what the image(s) show:"""
            
            response = self.llm.invoke(prompt)
            return response.content
        else:
            return f"The images appear to show: {context[:500]}..."
    
    def _generate_answer(self, context, question):
        """Generate general answer"""
        if self.llm:
            prompt = f"""Context: {context}
            
            Question: {question}
            
            Answer based on context:"""
            
            response = self.llm.invoke(prompt)
            return response.content
        else:
            return f"Based on the documents: {context[:500]}..."