import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class LLMHandler:
    """Handles LLM integration for RAG answers"""
    
    def __init__(self):
        self.llm = self._init_llm()
        self.embeddings = self._init_embeddings()
    
    def _init_llm(self):
            """Initialize LLM (Groq preferred for speed, but can use others)"""
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key and groq_api_key != "your_groq_api_key_here":
                    from langchain_groq import ChatGroq
                    print("INFO: Using Groq LLM")
                    return ChatGroq(
                        model="llama-3.3-70b-versatile", 
                        groq_api_key=groq_api_key,
                        temperature=0.1,
                        max_tokens=500
                    )

    def _init_embeddings(self):
            
            """Initialize embeddings for query"""
            nomic_api_key = os.getenv("NOMIC_API_KEY")
            if nomic_api_key and nomic_api_key != "your_nomic_api_key_here":
                    
                    from langchain_nomic import NomicEmbeddings
                    return NomicEmbeddings(
                        model="nomic-embed-text-v1",
                        nomic_api_key=nomic_api_key
                    )

    def generate_answer(self, question: str, context_chunks: List[str], metadata: List[Dict] = None) -> str:
            
            """Generate answer using LLM with RAG context"""
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_classic.schema import HumanMessage , SystemMessage
                
            # Prepare the context
            formatted_context = self._format_context(context_chunks, metadata)
                
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are a helpful AI assistant that answers questions based on provided document excerpts.
                    Use ONLY the information from the provided context to answer the question.
                    If the context doesn't contain relevant information, say "I cannot find that information in the document."
                    Keep answers concise and accurate."""),
                    HumanMessage(content=f"""Context from document:
                    {formatted_context}
                    
                    Question: {question}
                    
                    Based on the above context, provide a clear answer:""")
                ])
                
                # Generate answer
            messages = prompt.format_messages()
            response = self.llm.invoke(messages)
                
            return response.content.strip()
            
       
    
    def _format_context(self, chunks: List[str], metadata: List[Dict] = None) -> str:
            
            """Format context chunks for LLM"""
            formatted = []
            for i, chunk in enumerate(chunks):
                source_info = ""
                if metadata and i < len(metadata):
                    doc_id = metadata[i].get('document_id', 'Unknown')
                    chunk_idx = metadata[i].get('chunk_index', i)
                    source_info = f"\n[Source: Document {doc_id[:8]}..., Chunk {chunk_idx}]"
                
                formatted.append(f"--- Excerpt {i+1} ---{source_info}\n{chunk}\n")
            
            return "\n".join(formatted)
