from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.config import settings
from api.routes import router

# Validate environment
settings.validate_environment()

# Create FastAPI app
app = FastAPI(
    title="Document AI Backend",
    version="1.0.0",
    description="Multi-agent document intelligence system with RAG"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Document AI Backend API",
        "status": "running",
        "endpoints": {
            "upload": "/api/upload",
            "ask": "/api/ask",
            "documents": "/api/documents",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on changes
    )