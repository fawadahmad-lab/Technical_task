
---

## Document AI Backend - Multi-Agent RAG System

---

A backend system that processes **PDFs and images**, extracts and indexes their content using **AI agents**, and answers user questions through a **REST API** using **Retrieval-Augmented Generation (RAG)**.

---

##  System Architecture Overview

### High-Level Architecture

```
    User
    │
    ▼
    FastAPI REST API
    │
    ▼
    Agent Orchestration Layer
    │
    ├── Ingestion Agent
    ├── Indexing Agent
    └── QA Agent
    │
    ▼
    Vector Store (FAISS) ──► LLM (Groq)
    │
    ▼
    Response

```

---

### Processing Flow

1. **Upload Phase**
   - Client uploads a PDF or image
   - File is stored locally
   - Metadata is saved in SQLite

2. **Processing Phase**
   - Text extraction (PDF / OCR)
   - Text cleaning & normalization
   - Chunking and embedding generation
   - Storage in FAISS vector index

3. **Query Phase**
   - User submits a question
   - Relevant chunks retrieved via vector search
   - Context passed to LLM
   - Final answer returned

---

```

---

## Agent Responsibilities

###  Ingestion Agent
**Purpose:** Extract text from uploaded documents.

**Responsibilities**
- Detect file type (PDF or image)
- Extract text from PDFs using PyPDF2
- Perform OCR on images using Tesseract
- Clean and normalize extracted text

---

###  Indexing Agent
**Purpose:** Prepare extracted text for retrieval.

**Responsibilities**
- Split text into chunks (1000 chars, 200 overlap)
- Generate embeddings
- Store vectors in FAISS
- Maintain metadata links to original documents

---

### QA Agent
**Purpose:** Answer user questions using RAG.

**Responsibilities**
- Perform similarity search in FAISS
- Retrieve top-k relevant chunks
- Construct LLM prompt with context
- Generate answer and return sources

---

##  API Endpoints

### Base URL
```

[http://localhost:8000](http://localhost:8000)

```

---

### 1. Upload Document
**POST** `/api/upload`

Uploads and processes a PDF or image.

**Request**
```

multipart/form-data
file: <binary>

````

**Response**
```json
{
  "document_id": "uuid-string",
  "filename": "document.pdf",
  "status": "processed",
  "chunks_created": 5
}
````

---

### 2. Ask Question

**POST** `/api/ask`

**Request**

```json
{
  "question": "What is the tech stack?",
  "document_id": "optional-uuid"
}
```

**Response**

```json
{
  "question": "What is the tech stack?",
  "answer": "The system uses FastAPI, LangChain, and FAISS.",
  "sources": [
    {
      "score": 0.85,
      "metadata": {
        "document_id": "uuid",
        "chunk_id": "chunk_3"
      }
    }
  ]
}
```

---

### 3. List Documents

**GET** `/api/documents`

Returns all uploaded documents.

---

### 4. Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T10:30:00"
}
```

---

## Setup Instructions

### Prerequisites

* Python 3.10
* Tesseract OCR installed
* Groq API key

---

### 1. Clone & Setup

```bash
git clone <repository-url>
cd doc-ai-backend

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate  # macOS/Linux
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Configure Environment

Create `.env`:

```env
GROQ_API_KEY=your groq api key

NOMIC_API_KEY=your nomic api key

UPLOAD_DIR=uploads
VECTOR_STORE_DIR=vector_store
```

---

### 4. Install Tesseract OCR

* **Windows:** [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
* **macOS:** `brew install tesseract`
* **Linux:** `sudo apt-get install tesseract-ocr`

---

### 5. Run the Server

```bash
python app.py
```

Swagger Docs:

```
http://localhost:8000/docs
```

---

## Sample API Calls

### Upload PDF

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"
```

### Ask Question

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

### Ask About Specific Document

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the tech stack?",
    "document_id": "uuid-here"
  }'
```

### List Documents

```bash
curl -X GET http://localhost:8000/api/documents
```

---

## Trade-offs & Future Improvements

### Current Trade-offs

| Decision        | Reason                 | Impact                      |
| --------------- | ---------------------- | --------------------------- |
| FAISS (local)   | No external dependency | Not distributed             |
| SQLite          | Simple & lightweight   | Limited concurrency         |
| Sync processing | Easier error handling  | Slower uploads              |
| Basic OCR       | Offline & free         | Limited image understanding |
| Single LLM      | Simpler integration    | Vendor lock-in              |

---

### Future Improvements

**Short-term**

* Async background processing
* Better error handling
* Batch uploads

**Medium-term**

* PostgreSQL instead of SQLite
* Redis caching
* Hybrid search (keyword + vector)
* Authentication & rate limiting

**Long-term**

* Docker & Kubernetes
* Cloud vector databases
* Multi-LLM fallback
* Advanced OCR & multimodal RAG

---

## Summary

This project demonstrates a **modular, scalable, and production-oriented Document AI backend** using a **multi-agent RAG architecture**.
It is suitable for **technical assessments**, **portfolio demonstration**, or as a **foundation for real-world systems**.

---

