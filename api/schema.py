from pydantic import BaseModel
from typing import Optional, List

# Request schemas
class QuestionRequest(BaseModel):
    question: str
    document_id: Optional[str] = None

# Response schemas
class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunks_created: int = 0
    vector_store: str = ""

class QuestionResponse(BaseModel):
    question: str
    answer: str
    document_id: Optional[str] = None
    sources: List[dict] = []

class DocumentResponse(BaseModel):
    id: str
    filename: str
    type: str
    processed: bool
    created_at: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str