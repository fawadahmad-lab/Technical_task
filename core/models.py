from pydantic import BaseModel
from typing import Optional

class QuestionRequest(BaseModel):
    question: str
    document_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the tech stack?",
                "document_id": "optional-document-id"
            }
        }

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunks_created: Optional[int] = 0
    vector_store: Optional[str] = ""

class QuestionResponse(BaseModel):
    question: str
    answer: str
    document_id: Optional[str] = None
    sources: list = []

class DocumentInfo(BaseModel):
    id: str
    filename: str
    type: str
    processed: bool
    created_at: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str