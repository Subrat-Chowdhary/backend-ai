#!/usr/bin/env python3
"""
MVP version of Resume Matching System
- upload_profile: Upload single/multiple/zipped files to MinIO with category organization
- search_profile: Vectorized search using embeddings
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional
import logging
import os
import zipfile
import tempfile
import shutil
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Resume Matching System MVP")
    
    # Initialize services
    try:
        await initialize_services()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
    
    yield
    logger.info("Shutting down Resume Matching System MVP")

async def initialize_services():
    """Initialize MinIO buckets and Qdrant collections"""
    from services.storage_service import storage_service
    from services.vector_service import vector_service
    
    # Create MinIO buckets for each job role
    job_roles = ["Backend", "Frontend", "Database", "QA", "Fullstack", "DevOps", "Mobile", "DataScience"]
    for role in job_roles:
        bucket_name = f"resumes-{role.lower()}"
        await storage_service.create_bucket_if_not_exists(bucket_name)
    
    # Initialize vector collections
    await vector_service.initialize_collections()

# Create FastAPI application
app = FastAPI(
    title="Resume Matching System MVP",
    description="""
    MVP for Resume Matching with 2 core endpoints:
    
    ## 🚀 Core Features
    
    * **upload_profile**: Upload single/multiple/zipped resume files
    * **search_profile**: Vectorized search across uploaded resumes
    
    ## 📁 File Organization
    
    Files are organized by job categories in MinIO buckets:
    - resumes-backend
    - resumes-frontend  
    - resumes-database
    - resumes-qa
    - resumes-fullstack
    - resumes-devops
    - resumes-mobile
    - resumes-datascience
    """,
    version="1.0.0-mvp",
    lifespan=lifespan
)

# Custom CORS middleware
class CORSHandler(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

# Add CORS middleware
app.add_middleware(CORSHandler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Resume Matching System MVP",
        "version": "1.0.0-mvp",
        "endpoints": {
            "upload": "/upload_profile",
            "search": "/search_profile"
        },
        "docs": "/docs"
    }

@app.options("/upload_profile")
async def upload_profile_options():
    """Handle preflight requests"""
    return {"message": "OK"}

@app.post("/upload_profile")
async def upload_profile(
    files: List[UploadFile] = File(...),
    job_category: str = Form(..., description="Job category: Backend, Frontend, Database, QA, Fullstack, DevOps, Mobile, DataScience"),
    description: Optional[str] = Form(None, description="Optional description for the upload batch")
):
    """
    Upload single/multiple/zipped resume files
    
    - **files**: List of files (PDF, DOCX, DOC) or ZIP files
    - **job_category**: Target job category for organization (use: Backend, Frontend, Database, QA, Fullstack, DevOps, Mobile, DataScience)
    - **description**: Optional batch description
    """
    try:
        logger.info(f"Upload request received - Category: {job_category}, Files: {[f.filename for f in files]}")
        from services.storage_service import storage_service
        from services.document_service import document_service
        from services.vector_service import vector_service
        
        # Validate job category
        valid_categories = ["Backend", "Frontend", "Database", "QA", "Fullstack", "DevOps", "Mobile", "DataScience"]
        if job_category not in valid_categories:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid job category. Must be one of: {valid_categories}"
            )
        
        uploaded_files = []
        failed_files = []
        processed_count = 0
        
        for file in files:
            try:
                # Check file size (10MB limit)
                if file.size > 10485760:
                    failed_files.append({
                        "filename": file.filename,
                        "error": "File size exceeds 10MB limit"
                    })
                    continue
                
                # Handle ZIP files
                if file.filename.lower().endswith('.zip'):
                    zip_results = await process_zip_file(file, job_category)
                    uploaded_files.extend(zip_results["uploaded"])
                    failed_files.extend(zip_results["failed"])
                    processed_count += zip_results["processed_count"]
                else:
                    # Handle single file
                    result = await process_single_file(file, job_category)
                    if result["success"]:
                        uploaded_files.append(result["file_info"])
                        processed_count += 1
                    else:
                        failed_files.append({
                            "filename": file.filename,
                            "error": result["error"]
                        })
            
            except Exception as e:
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "message": "Upload completed",
            "job_category": job_category,
            "total_files_processed": len(files),
            "successful_uploads": len(uploaded_files),
            "failed_uploads": len(failed_files),
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.options("/search_profile")
async def search_profile_options():
    """Handle preflight requests"""
    return {"message": "OK"}

@app.post("/search_profile")
async def search_profile(
    query: str = Form(..., description="Search query or job description"),
    job_category: Optional[str] = Form(None, description="Filter by job category (use: Backend, Frontend, Database, QA, Fullstack, DevOps, Mobile, DataScience)"),
    limit: int = Form(10, description="Maximum number of results"),
    similarity_threshold: float = Form(0.7, description="Minimum similarity score (0.0 to 1.0)")
):
    """
    Vectorized search across uploaded resumes
    
    - **query**: Search query or job description text
    - **job_category**: Optional filter by specific job category (use: Backend, Frontend, Database, QA, Fullstack, DevOps, Mobile, DataScience)
    - **limit**: Maximum number of results to return
    - **similarity_threshold**: Minimum similarity score for results
    """
    try:
        logger.info(f"Search request received - Query: {query}, Category: {job_category}")
        from services.vector_service import vector_service
        
        # Perform vectorized search
        search_results = await vector_service.search_resumes(
            query_text=query,
            job_category=job_category,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "query": query,
            "job_category": job_category,
            "total_results": len(search_results),
            "similarity_threshold": similarity_threshold,
            "results": search_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_zip_file(zip_file: UploadFile, job_category: str):
    """Process ZIP file and extract individual resumes"""
    uploaded = []
    failed = []
    processed_count = 0
    
    try:
        # Save ZIP file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            content = await zip_file.read()
            temp_zip.write(content)
            temp_zip_path = temp_zip.name
        
        # Extract ZIP file
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            extract_dir = tempfile.mkdtemp()
            zip_ref.extractall(extract_dir)
            
            # Process each extracted file
            for root, dirs, files in os.walk(extract_dir):
                for filename in files:
                    if filename.lower().endswith(('.pdf', '.docx', '.doc')):
                        file_path = os.path.join(root, filename)
                        
                        try:
                            # Create UploadFile-like object
                            with open(file_path, 'rb') as f:
                                file_content = f.read()
                            
                            # Process the file
                            result = await process_file_content(
                                filename=filename,
                                content=file_content,
                                job_category=job_category
                            )
                            
                            if result["success"]:
                                uploaded.append(result["file_info"])
                                processed_count += 1
                            else:
                                failed.append({
                                    "filename": filename,
                                    "error": result["error"]
                                })
                        
                        except Exception as e:
                            failed.append({
                                "filename": filename,
                                "error": str(e)
                            })
        
        # Cleanup
        os.unlink(temp_zip_path)
        shutil.rmtree(extract_dir)
    
    except Exception as e:
        failed.append({
            "filename": zip_file.filename,
            "error": f"ZIP processing failed: {str(e)}"
        })
    
    return {
        "uploaded": uploaded,
        "failed": failed,
        "processed_count": processed_count
    }

async def process_single_file(file: UploadFile, job_category: str):
    """Process a single uploaded file"""
    try:
        # Validate file extension
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
            return {
                "success": False,
                "error": "Invalid file type. Only PDF, DOCX, DOC files are allowed."
            }
        
        # Read file content
        content = await file.read()
        
        # Process file content
        return await process_file_content(
            filename=file.filename,
            content=content,
            job_category=job_category
        )
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def process_file_content(filename: str, content: bytes, job_category: str):
    """Process file content - upload to MinIO and create embeddings"""
    try:
        from services.storage_service import storage_service
        from services.document_service import document_service
        from services.vector_service import vector_service
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        # Upload to MinIO
        bucket_name = f"resumes-{job_category.lower()}"
        minio_path = await storage_service.upload_file(
            bucket_name=bucket_name,
            object_name=unique_filename,
            file_content=content
        )
        
        # Extract text from document
        text_content = await document_service.extract_text(content, filename)
        
        # Create embedding and store in vector database
        embedding_id = await vector_service.add_document(
            text=text_content,
            metadata={
                "filename": filename,
                "unique_filename": unique_filename,
                "job_category": job_category,
                "minio_path": minio_path,
                "upload_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "success": True,
            "file_info": {
                "original_filename": filename,
                "unique_filename": unique_filename,
                "job_category": job_category,
                "minio_path": minio_path,
                "embedding_id": embedding_id,
                "file_size": len(content),
                "upload_timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"File processing error for {filename}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from services.storage_service import storage_service
        from services.vector_service import vector_service
        
        # Check MinIO
        minio_status = await storage_service.health_check()
        
        # Check Qdrant
        qdrant_status = await vector_service.health_check()
        
        overall_status = "healthy" if minio_status and qdrant_status else "degraded"
        
        return {
            "status": overall_status,
            "services": {
                "minio": "healthy" if minio_status else "unhealthy",
                "qdrant": "healthy" if qdrant_status else "unhealthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/debug/collection")
async def debug_collection():
    """Debug collection status"""
    try:
        from services.vector_service import vector_service
        info = await vector_service.get_collection_info()
        return {
            "collection_info": info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/debug/force_indexing")
async def force_indexing():
    """Force immediate indexing"""
    try:
        from services.vector_service import vector_service
        result = await vector_service.force_indexing()
        return {
            "success": result,
            "message": "Force indexing completed" if result else "Force indexing failed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/debug/rebuild_index")
async def rebuild_index():
    """Rebuild vector index"""
    try:
        from services.vector_service import vector_service
        result = await vector_service.rebuild_index()
        return {
            "success": result,
            "message": "Index rebuild completed" if result else "Index rebuild failed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app_mvp:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )