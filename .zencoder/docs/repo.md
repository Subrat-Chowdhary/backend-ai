# AI-Powered Resume Matching System Information

## Summary
A comprehensive AI-driven platform for HR teams and consulting firms to efficiently shortlist candidates from large pools of resumes using semantic search and NLP. The system provides resume upload, intelligent parsing, semantic search, job role categorization, and background processing capabilities.

## Structure
- **app/**: Main application code with FastAPI implementation
  - **api/**: API route definitions for resume and job endpoints
  - **models/**: Database models and SQLAlchemy setup
  - **schemas/**: Pydantic models for request/response validation
  - **services/**: Core services for file handling, document parsing, and vector search
  - **tasks/**: Background processing tasks using Celery
- **uploads/**: Directory for storing uploaded resume files
- **services/**: Additional standalone services

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
- pydantic==2.5.0: Data validation and settings management
- sentence-transformers==5.0.0: ML model for text embeddings
- PyPDF2==3.0.1: PDF parsing library
- python-docx==1.1.0: DOCX parsing library
- minio==7.2.15: S3-compatible object storage client
- httpx==0.28.1: HTTP client for Python

**Infrastructure Dependencies**:
- PostgreSQL: Database for storing resume metadata
- Redis: Message broker for Celery tasks
- Qdrant: Vector database for similarity search
- MinIO: Object storage for resume files

## Build & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application locally
uvicorn app.main:app --reload

# Run with Docker Compose
docker-compose up -d
```

## Docker
**Dockerfile**: Dockerfile (Python 3.11-slim base image)
**Docker Compose**: docker-compose.yml
**Services**:
- resume-api: Main application service
- postgres: PostgreSQL database
- redis: Redis for message queue
- qdrant: Vector database
- minio: Object storage

**Configuration**:
- Environment variables for service connections
- Volume mounts for persistent data
- Health checks for all services
- Exposed ports for each service

## Main Files
**Entry Point**: app/main.py
**Configuration**: app/config.py
**Database Setup**: app/models/database.py
**API Routes**:
- app/api/resume_routes.py: Resume upload and search endpoints
- app/api/job_routes.py: Job description endpoints

**Core Services**:
- app/services/file_service.py: File storage and retrieval
- app/services/document_parser.py: Resume parsing and information extraction
- app/services/vector_service.py: Vector embeddings and similarity search

## Testing
**Test Files**:
- test_setup.py: Verifies system setup and dependencies
- test_api.py: Tests API endpoints
- test_basic_setup.py: Basic setup verification
- test_enhanced_extraction.py: Tests document extraction features

**Run Command**:
```bash
# Run setup tests
python test_setup.py

# Run API tests
python test_api.py
```