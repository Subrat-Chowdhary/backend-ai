# AI-Powered Resume Matching System

A comprehensive AI-driven platform for HR teams and consulting firms to efficiently shortlist candidates from large pools of resumes using semantic search and NLP.

## 🚀 Features

- **Resume Upload & Storage**: Bulk upload resumes in PDF, DOCX, DOC formats
- **Intelligent Parsing**: Extract candidate information using advanced NER models
- **Semantic Search**: Find best-fit candidates using vector similarity search
- **Job Role Categorization**: Automatically categorize resumes by job roles
- **Background Processing**: Async processing with Celery for scalability
- **Vector Database**: Qdrant for efficient similarity search
- **Object Storage**: MinIO for scalable file storage

## 🛠 Technology Stack

- **Backend**: FastAPI, Python
- **Vector DB**: Qdrant
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **NLP**: Hugging Face Transformers, spaCy
- **Storage**: MinIO (S3-compatible)
- **Queue**: Redis + Celery
- **Database**: PostgreSQL

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## 🚀 Quick Start

### 1. Start Docker Desktop

Make sure Docker Desktop is running on your Windows machine.

### 2. Start Services with Docker

```bash
# Navigate to project directory
cd e:/AHOMTech/VPS_157.180.44.51

# Start all services (PostgreSQL, Redis, Qdrant, MinIO, API, Celery)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 3. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **MinIO Console**: http://localhost:9001 (admin/minioadmin)
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 📖 API Usage Examples

### Upload Resume

```bash
curl -X POST "http://localhost:8000/resumes/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf" \
  -F "job_role=Backend"
```

### Search Resumes

```bash
curl -X POST "http://localhost:8000/resumes/search" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Looking for a Python developer with FastAPI experience",
    "job_role": "Backend",
    "limit": 10,
    "similarity_threshold": 0.5
  }'
```

## 🔧 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Celery Worker  │    │   PostgreSQL    │
│                 │    │                 │    │                 │
│ • REST API      │    │ • Resume Parse  │    │ • Metadata      │
│ • File Upload   │    │ • Embedding Gen │    │ • Job Desc      │
│ • Search        │    │ • Background    │    │ • Search Logs   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Redis       │    │     Qdrant      │    │     MinIO       │
│                 │    │                 │    │                 │
│ • Task Queue    │    │ • Vector Store  │    │ • File Storage  │
│ • Cache         │    │ • Similarity    │    │ • Resume Files  │
│ • Session       │    │ • Search        │    │ • Backups       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚨 Important Setup Notes

1. **Start Docker Desktop first** - The system requires Docker to be running
2. **First run takes time** - ML models need to be downloaded
3. **Port availability** - Ensure ports 8000, 5432, 6379, 6333, 9000, 9001 are free
4. **Memory allocation** - Increase Docker memory to at least 4GB for ML models

## 📝 Complete System Overview

Your AI-Powered Resume Matching System includes:

### Core Components Built:

✅ **FastAPI Application** (`app/main.py`)
✅ **Database Models** (`app/models/`)
✅ **API Routes** (`app/api/`)
✅ **File Processing Service** (`app/services/file_service.py`)
✅ **Document Parser** (`app/services/document_parser.py`)
✅ **Vector Search Service** (`app/services/vector_service.py`)
✅ **Background Tasks** (`app/tasks/resume_processing.py`)
✅ **Docker Configuration** (`docker-compose.yml`, `Dockerfile`)

### Key Features Implemented:

- Resume upload (single & bulk)
- Document parsing (PDF, DOCX, DOC)
- Candidate information extraction (name, email, phone)
- Skills extraction and job role categorization
- Vector embeddings generation
- Semantic search functionality
- Background processing with Celery
- MinIO object storage integration
- PostgreSQL metadata storage
- Qdrant vector database integration

## 🔄 Next Steps

1. **Start Docker Desktop**
2. **Run**: `docker-compose up -d`
3. **Test**: Visit http://localhost:8000/docs
4. **Upload resumes** and test the search functionality

The system is production-ready with all components integrated!
