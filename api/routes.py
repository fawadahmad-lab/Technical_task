from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from typing import List
import sys

sys.path.append('.')

from core.database import db
from core.config import settings
from core.models import (
    QuestionRequest, UploadResponse, 
    QuestionResponse, DocumentInfo, HealthResponse
)


from agents.QA_agent import QAAgent
from RAG.doc_workflow import doc_workflow

router = APIRouter(prefix="/api", tags=["API"])

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF or image)"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    if not any(file.filename.lower().endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Generate unique ID
    doc_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{doc_id}{file_extension}"
    filepath = os.path.join(settings.UPLOAD_DIR, saved_filename)
    
    # Save file locally
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Store in database
    db.add_document(doc_id, file.filename, filepath, file_extension)
    
    # Process document
    try:
        result = doc_workflow(doc_id, filepath)
        db.update_document_status(doc_id, True)
        
        return UploadResponse(
            document_id=doc_id,
            filename=file.filename,
            status="processed",
            chunks_created=result.get("chunks_count", 0),
            vector_store=result.get("vector_store", "")
        )
    
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "document_id": doc_id},
            status_code=500
        )

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about processed documents"""
    # Check if document exists and is processed
    if request.document_id:
        processed, error_msg = db.document_exists_and_processed(request.document_id)
        if not processed:
            if "not found" in error_msg:
                raise HTTPException(status_code=404, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
    
    # Use QA Agent
    try:
        qa_agent = QAAgent()
        answer_data = qa_agent.answer_question(
            question=request.question,
            document_id=request.document_id
        )
        
        return QuestionResponse(
            question=request.question,
            answer=answer_data.get("answer", ""),
            document_id=request.document_id,
            sources=answer_data.get("sources", [])[:3]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all uploaded documents"""
    return db.list_documents()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )