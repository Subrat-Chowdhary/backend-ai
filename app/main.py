from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.models.database import engine, Base
from app.api.resume_routes import router as resume_router
from app.api.job_routes import router as job_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI-Powered Resume Matching System")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI-Powered Resume Matching System")


# Create FastAPI application
app = FastAPI(
    title="AI-Powered Resume Matching System",
    description="""
    A comprehensive AI-driven platform for HR teams and consulting firms to efficiently 
    shortlist candidates from large pools of resumes using semantic search and NLP.
    
    ## Features
    
    * **Resume Upload & Storage**: Bulk upload resumes in PDF, DOCX, DOC formats
    * **Intelligent Parsing**: Extract candidate information using advanced NER models
    * **Semantic Search**: Find best-fit candidates using vector similarity search
    * **Job Role Categorization**: Automatically categorize resumes by job roles
    * **Background Processing**: Async processing with Celery for scalability
    * **Vector Database**: Qdrant for efficient similarity search
    * **Object Storage**: MinIO for scalable file storage
    
    ## Technology Stack
    
    * **Backend**: FastAPI, Python
    * **Vector DB**: Qdrant
    * **Embeddings**: Sentence Transformers
    * **NLP**: Hugging Face Transformers, spaCy
    * **Storage**: MinIO (S3-compatible)
    * **Queue**: Redis + Celery
    * **Database**: PostgreSQL
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume_router)
app.include_router(job_router)


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI-Powered Resume Matching System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from app.models.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    try:
        # Check Redis connection
        import redis
        r = redis.from_url(settings.redis_url)
        r.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    try:
        # Check Qdrant connection
        from app.services.vector_service import vector_service
        collections = vector_service.qdrant_client.get_collections()
        qdrant_status = "healthy"
    except Exception as e:
        qdrant_status = f"unhealthy: {str(e)}"
    
    try:
        # Check MinIO connection
        from app.services.file_service import file_service
        file_service.minio_client.list_buckets()
        minio_status = "healthy"
    except Exception as e:
        minio_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if all("healthy" in status for status in [db_status, redis_status, qdrant_status, minio_status]) else "degraded",
        "services": {
            "database": db_status,
            "redis": redis_status,
            "qdrant": qdrant_status,
            "minio": minio_status
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/config")
async def get_config():
    """Get system configuration (non-sensitive)"""
    return {
        "job_roles": settings.job_roles_list,
        "allowed_extensions": settings.allowed_extensions_list,
        "max_file_size": settings.max_file_size,
        "embedding_model": settings.embedding_model,
        "upload_dir": settings.upload_dir
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )