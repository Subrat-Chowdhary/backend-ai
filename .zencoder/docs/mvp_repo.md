# AI-Powered Resume Matching System - MVP Information

## Summary
A streamlined MVP version of the AI-driven resume matching system focused on two core functionalities: resume upload and semantic search. The system allows uploading resumes in various formats and performs vector-based similarity search to find the best matching candidates.

## Structure
- **app_mvp.py**: Main application entry point for the MVP version
- **services/**: Core services for the MVP implementation
  - **document_service.py**: Text extraction from PDF/DOCX files
  - **storage_service.py**: MinIO integration for file storage
  - **vector_service.py**: Vector embeddings and Qdrant integration
- **uploads/**: Directory for temporary file storage

## Language & Runtime
**Language**: Python
**Version**: 3.11 (specified in Dockerfile)
**Framework**: FastAPI 0.104.1
**Build System**: Docker
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- fastapi==0.104.1: Web framework for building APIs
- uvicorn==0.24.0: ASGI server for FastAPI
- python-multipart==0.0.6: For handling file uploads
- pydantic==2.5.0: Data validation
- PyPDF2==3.0.1: PDF parsing library
- python-docx==1.1.0: DOCX parsing library
- minio==7.2.15: S3-compatible object storage client
- sentence-transformers==5.0.0: ML model for text embeddings
- httpx==0.28.1: HTTP client for Python

**Infrastructure Dependencies**:
- Qdrant: Vector database for similarity search
- MinIO: Object storage for resume files

## Build & Installation
```bash
# Install MVP dependencies
pip install -r requirements-mvp.txt

# Run the MVP application locally
python app_mvp.py

# Run with Docker Compose (MVP version)
docker-compose -f docker-compose.mvp.yml up -d
```

## Docker
**Docker Compose**: docker-compose.mvp.yml
**Services**:
- resume-api: Main application service
- qdrant: Vector database
- minio: Object storage

**Configuration**:
- Environment variables for service connections
- Volume mounts for persistent data
- Health checks for services
- Exposed ports: 8000 (API), 6333/6334 (Qdrant), 9000/9001 (MinIO)

## Main Files
**Entry Point**: app_mvp.py
**Core Services**:
- services/document_service.py: Text extraction from documents
- services/storage_service.py: File storage using MinIO
- services/vector_service.py: Vector embeddings and search using Qdrant

## API Endpoints
**Upload Endpoint**:
- POST /upload_profile: Upload single/multiple/zipped resume files
  - Parameters: files, job_category, description

**Search Endpoint**:
- POST /search_profile: Vectorized search across uploaded resumes
  - Parameters: query, job_category, limit, similarity_threshold

## MVP Features
- Resume upload (single, multiple, and ZIP files)
- Document parsing (PDF, DOCX, DOC)
- File organization by job categories
- Vector embeddings generation
- Semantic search functionality
- MinIO object storage integration
- Qdrant vector database integration

## Differences from Full Version
- No PostgreSQL database (metadata stored in Qdrant)
- No Redis/Celery for background processing
- Simplified architecture with fewer dependencies
- Focus on core upload and search functionality
- No advanced candidate information extraction
- Streamlined Docker setup with fewer services