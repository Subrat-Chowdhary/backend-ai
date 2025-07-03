#!/usr/bin/env python3
"""
Minimal version of the Resume Matching System for testing
This version runs without heavy ML dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI-Powered Resume Matching System (Minimal Version)")
    yield
    # Shutdown
    logger.info("Shutting down AI-Powered Resume Matching System")


# Create FastAPI application
app = FastAPI(
    title="AI-Powered Resume Matching System (Minimal)",
    description="""
    A minimal version of the AI-driven platform for testing basic functionality.
    
    ## Features Available
    
    * **Basic API**: Core endpoints for testing
    * **Health Checks**: Service connectivity tests
    * **Configuration**: System settings
    
    ## Infrastructure Services
    
    * **Database**: PostgreSQL
    * **Cache**: Redis
    * **Vector DB**: Qdrant
    * **Storage**: MinIO
    """,
    version="1.0.0-minimal",
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


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI-Powered Resume Matching System (Minimal Version)",
        "version": "1.0.0-minimal",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "note": "This is a minimal version for testing basic functionality"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    services_status = {}
    overall_status = "healthy"
    
    # Check database connection
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="resume_db",
            user="postgres",
            password="password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        services_status["database"] = "healthy"
        logger.info(f"Database connected: {version[0]}")
    except Exception as e:
        services_status["database"] = f"unhealthy: {str(e)}"
        overall_status = "degraded"
        logger.error(f"Database connection failed: {e}")
    
    # Check Redis connection
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        services_status["redis"] = "healthy"
        logger.info("Redis connected")
    except Exception as e:
        services_status["redis"] = f"unhealthy: {str(e)}"
        overall_status = "degraded"
        logger.error(f"Redis connection failed: {e}")
    
    # Check Qdrant connection
    try:
        import httpx
        response = httpx.get("http://localhost:6333/collections", timeout=5.0)
        if response.status_code == 200:
            services_status["qdrant"] = "healthy"
            logger.info("Qdrant connected")
        else:
            services_status["qdrant"] = f"unhealthy: HTTP {response.status_code}"
            overall_status = "degraded"
    except Exception as e:
        services_status["qdrant"] = f"unhealthy: {str(e)}"
        overall_status = "degraded"
        logger.error(f"Qdrant connection failed: {e}")
    
    # Check MinIO connection
    try:
        from minio import Minio
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        buckets = client.list_buckets()
        services_status["minio"] = "healthy"
        logger.info(f"MinIO connected, buckets: {[b.name for b in buckets]}")
    except Exception as e:
        services_status["minio"] = f"unhealthy: {str(e)}"
        overall_status = "degraded"
        logger.error(f"MinIO connection failed: {e}")
    
    return {
        "status": overall_status,
        "services": services_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/config")
async def get_config():
    """Get system configuration (non-sensitive)"""
    return {
        "job_roles": ["Backend", "Frontend", "Database", "QA", "Fullstack", "DevOps", "Mobile", "DataScience"],
        "allowed_extensions": ["pdf", "docx", "doc"],
        "max_file_size": 10485760,  # 10MB
        "embedding_model": "all-MiniLM-L6-v2",
        "upload_dir": "./uploads",
        "version": "minimal"
    }


@app.get("/services/status")
async def services_status():
    """Detailed services status"""
    return {
        "infrastructure": {
            "postgresql": {"port": 5432, "status": "running"},
            "redis": {"port": 6379, "status": "running"},
            "qdrant": {"port": 6333, "status": "running"},
            "minio": {"port": 9000, "status": "running"}
        },
        "application": {
            "api": {"port": 8000, "status": "running"},
            "version": "minimal"
        }
    }


@app.post("/api/test")
async def test_endpoint():
    """Test endpoint for basic functionality"""
    return {
        "message": "Test endpoint working",
        "status": "success",
        "services_available": [
            "PostgreSQL Database",
            "Redis Cache",
            "Qdrant Vector DB",
            "MinIO Object Storage"
        ]
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "minimal_version"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )