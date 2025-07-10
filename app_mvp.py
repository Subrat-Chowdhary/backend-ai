#!/usr/bin/env python3
"""
MVP version of Resume Upload System
- upload_profile: Upload single/multiple/zipped files to MinIO with category organization
"""
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional
import logging
import os
import zipfile
import tempfile
import shutil
from datetime import datetime
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Resume Upload System")
    try:
        await initialize_services()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
    yield
    logger.info("Shutting down Resume Upload System")

async def initialize_services():
    from services.storage_service import storage_service
    default_bucket = "rawresumes"
    await storage_service.create_bucket_if_not_exists(default_bucket)
    logger.info(f"Default bucket ready: {default_bucket}")

# FastAPI app init
app = FastAPI(
    title="Resume Upload System New",
    description="""
    Minimal Resume Upload System

    ## Core Features

    - **upload_profile**: Upload single/multiple/zipped resume files with optional category-based bucket organization

    ## File Organization

    - No category: Files go to default `rawresumes` bucket
    - With category: Files go to `resumes-{category}` bucket (e.g., `resumes-backend`)
    """,
    version="1.0.0-mvp",
    lifespan=lifespan
)

class CORSHandler(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

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
    return {
        "message": "Resume Upload System - Dynamic Upload Service",
        "version": "1.0.0-mvp",
        "service_type": "Dynamic File Upload Service",
        "endpoints": {
            "upload": "/upload_profile",
            "health": "/health",
            "debug": "/debug/buckets"
        },
        "supported_formats": ["PDF", "DOC", "DOCX", "TXT", "ZIP"],
        "max_file_size": "10MB",
        "bucket_organization": {
            "default": "rawresumes (when no category specified)",
            "category_based": "resumes-{category} (when category specified)",
            "conflict_handling": "Use existing bucket or create timestamped bucket"
        }
    }

async def determine_bucket_name(job_category: Optional[str], use_existing_bucket: bool) -> dict:
    from services.storage_service import storage_service
    if not job_category:
        return {
            "bucket_name": "rawresumes",
            "status": "using_default_bucket",
            "message": "No category specified, using default bucket"
        }
    import re
    clean_category = re.sub(r'[^a-zA-Z0-9]', '', job_category.lower())
    base_bucket_name = f"resumes-{clean_category}"
    try:
        bucket_exists = await storage_service.bucket_exists(base_bucket_name)
        if bucket_exists:
            if use_existing_bucket:
                return {
                    "bucket_name": base_bucket_name,
                    "status": "using_existing_bucket",
                    "message": f"Using existing bucket for category '{job_category}'"
                }
            else:
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                unique_bucket_name = f"{base_bucket_name}-{timestamp}"
                await storage_service.create_bucket_if_not_exists(unique_bucket_name)
                return {
                    "bucket_name": unique_bucket_name,
                    "status": "created_new_bucket",
                    "message": f"Created new bucket '{unique_bucket_name}' for category '{job_category}'"
                }
        else:
            await storage_service.create_bucket_if_not_exists(base_bucket_name)
            return {
                "bucket_name": base_bucket_name,
                "status": "created_new_bucket",
                "message": f"Created new bucket '{base_bucket_name}' for category '{job_category}'"
            }
    except Exception as e:
        logger.error(f"Error determining bucket name: {e}")
        return {
            "bucket_name": "rawresumes",
            "status": "fallback_to_default",
            "message": f"Error with category bucket, using default: {str(e)}"
        }

@app.options("/upload_profile")
async def upload_profile_options():
    return {"message": "OK"}

@app.post("/upload_profile")
async def upload_profile(
    files: List[UploadFile] = File(...),
    job_category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    use_existing_bucket: bool = Form(True)
):
    try:
        logger.info(f"Upload request - Files: {[f.filename for f in files]}, Category: {job_category}")
        from services.storage_service import storage_service
        bucket_info = await determine_bucket_name(job_category, use_existing_bucket)
        bucket_name = bucket_info["bucket_name"]
        logger.info(f"Using bucket: {bucket_name} ({bucket_info['status']})")
        uploaded_files, rejected_files, total_files_processed = [], [], 0

        for file in files:
            try:
                if file.size and file.size > 10485760:
                    rejected_files.append({
                        "filename": file.filename,
                        "reason": "File size exceeds 10MB limit",
                        "file_size_mb": round(file.size / 1048576, 2)
                    })
                    continue
                if file.filename.lower().endswith('.zip'):
                    zip_results = await process_zip_file_raw(file, bucket_name)
                    uploaded_files.extend(zip_results["uploaded"])
                    rejected_files.extend(zip_results["rejected"])
                    total_files_processed += zip_results["total_processed"]
                else:
                    total_files_processed += 1
                    result = await process_single_file_raw(file, bucket_name)
                    if result["success"]:
                        uploaded_files.append(result["file_info"])
                    else:
                        rejected_files.append({
                            "filename": file.filename,
                            "reason": result["error"]
                        })
            except Exception as e:
                rejected_files.append({
                    "filename": file.filename,
                    "reason": f"Processing error: {str(e)}"
                })

        success_count = len(uploaded_files)
        rejected_count = len(rejected_files)
        if success_count > 0 and rejected_count == 0:
            message = f"🎉 Excellent! All {success_count} file(s) uploaded successfully!"
            status_message = "✅ Your files are now ready for further processing. We will notify you when your files are processed and ready for search operation."
        elif success_count > 0 and rejected_count > 0:
            message = f"⚠️ Partial Upload Complete: {success_count} file(s) uploaded, {rejected_count} file(s) rejected"
            status_message = f"✅ {success_count} files uploaded. ❌ {rejected_count} files rejected."
        else:
            message = f"❌ Upload Failed: All {rejected_count} file(s) were rejected"
            status_message = "Sorry, could not process your files."

        return {
            "success": success_count > 0,
            "message": message,
            "status_message": status_message,
            "bucket_info": bucket_info,
            "summary": {
                "total_files_submitted": len(files),
                "total_files_processed": total_files_processed,
                "successful_uploads": success_count,
                "rejected_files": rejected_count
            },
            "uploaded_files": uploaded_files,
            "rejected_files": rejected_files,
            "job_category": job_category,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"🚨 Server Error: {str(e)}"
        )

async def process_zip_file_raw(zip_file: UploadFile, bucket_name: str):
    uploaded, rejected, total_processed = [], [], 0
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            content = await zip_file.read()
            temp_zip.write(content)
            temp_zip_path = temp_zip.name
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            extract_dir = tempfile.mkdtemp()
            zip_ref.extractall(extract_dir)
            for root, dirs, files in os.walk(extract_dir):
                for filename in files:
                    if filename.startswith('.') or filename.startswith('__'):
                        continue
                    total_processed += 1
                    file_path = os.path.join(root, filename)
                    if not filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
                        rejected.append({
                            "filename": filename,
                            "reason": f"Unsupported file format."
                        })
                        continue
                    try:
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        if len(file_content) > 10485760:
                            rejected.append({
                                "filename": filename,
                                "reason": "File size exceeds 10MB limit",
                                "file_size_mb": round(len(file_content) / 1048576, 2)
                            })
                            continue
                        result = await upload_file_to_bucket(
                            filename=filename,
                            content=file_content,
                            bucket_name=bucket_name
                        )
                        if result["success"]:
                            uploaded.append(result["file_info"])
                        else:
                            rejected.append({
                                "filename": filename,
                                "reason": result["error"]
                            })
                    except Exception as e:
                        rejected.append({
                            "filename": filename,
                            "reason": f"Processing error: {str(e)}"
                        })
        os.unlink(temp_zip_path)
        shutil.rmtree(extract_dir)
    except Exception as e:
        rejected.append({
            "filename": zip_file.filename,
            "reason": f"ZIP extraction failed: {str(e)}"
        })
    return {
        "uploaded": uploaded,
        "rejected": rejected,
        "total_processed": total_processed
    }

async def process_single_file_raw(file: UploadFile, bucket_name: str):
    try:
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
            return {
                "success": False,
                "error": "Unsupported file format."
            }
        content = await file.read()
        return await upload_file_to_bucket(
            filename=file.filename,
            content=content,
            bucket_name=bucket_name
        )
    except Exception as e:
        return {
            "success": False,
            "error": f"File processing error: {str(e)}"
        }

async def upload_file_to_bucket(filename: str, content: bytes, bucket_name: str):
    try:
        from services.storage_service import storage_service
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        file_extension = filename.split('.')[-1].lower()
        base_name = '.'.join(filename.split('.')[:-1])
        unique_filename = f"{timestamp}_{base_name}.{file_extension}"
        minio_path = await storage_service.upload_file(
            bucket_name=bucket_name,
            object_name=unique_filename,
            file_content=content
        )
        logger.info(f"File uploaded to bucket {bucket_name}: {minio_path}")
        return {
            "success": True,
            "file_info": {
                "original_filename": filename,
                "unique_filename": unique_filename,
                "minio_path": minio_path,
                "bucket_name": bucket_name,
                "file_size_bytes": len(content),
                "file_size_mb": round(len(content) / 1048576, 2),
                "upload_timestamp": datetime.utcnow().isoformat(),
                "status": f"uploaded_to_bucket_{bucket_name}"
            }
        }
    except Exception as e:
        logger.error(f"Raw file upload error for {filename}: {e}")
        return {
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }


@app.post("/search_profile")
async def search_profile(
    query: str = Form(..., description="Search query or job description"),
    limit: int = Form(10, description="Maximum number of results"),
    similarity_threshold: float = Form(0.7, description="Minimum similarity score (0.0 to 1.0)")
):
    """
    Proxy endpoint: Query Qdrant directly, return formatted search result
    """
    try:
        # Qdrant external URL (can be put in env/config)
        QDRANT_URL = "http://157.180.44.51:6333"
        COLLECTION_NAME = "employee_profiles"  # Or 'resumes', as per your setup

        # Convert query text to embedding
        # If you want to do local embedding, do it here. (Light version may skip it!)
        # For demo, let's say you already have embedding ready, or you use payload search

        # For now, using Qdrant's payload full-scan search (for demo)
        # Normally you would need to vectorize the query and use /search endpoint

        # ----
        # Example: Qdrant payload filter search (full scan)
        # For real vector search, need to POST to /collections/{collection}/points/search
        # ----

        search_payload = {
            "filter": {
                # Optionally add any payload-based filtering here
                # For example: "must": [{"key": "skills", "match": {"value": "python"}}]
            },
            "limit": limit,
            # "with_payload": True, # Uncomment if needed
            # "score_threshold": similarity_threshold, # If using vector search
        }

        # For real vector search, you need a vector embedding for your query!
        # Here, only using payload scan for sample.
        url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/scroll"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=search_payload)
            response.raise_for_status()
            qdrant_data = response.json()

        # Parse & format result
        result_points = qdrant_data.get("result", {}).get("points", [])
        results = []
        for point in result_points:
            # Qdrant returns 'id', 'payload', etc.
            results.append({
                "id": point.get("id"),
                **point.get("payload", {}),
                # add more if needed (like 'vector' if required)
            })

        return {
            "success": True,
            "query": query,
            "total_results": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/health")
async def health_check():
    try:
        from services.storage_service import storage_service
        minio_status = await storage_service.health_check()
        return {
            "status": "healthy" if minio_status else "unhealthy",
            "services": {
                "minio_storage": "healthy" if minio_status else "unhealthy"
            },
            "upload_service": "ready" if minio_status else "unavailable",
            "message": "Service ready" if minio_status else "Storage unavailable",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Health check failed",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/debug/buckets")
async def debug_buckets():
    try:
        from services.storage_service import storage_service
        all_buckets = await storage_service.list_all_buckets()
        bucket_status = {}
        total_files = 0
        for bucket_name in all_buckets:
            try:
                files = await storage_service.list_files(bucket_name)
                bucket_status[bucket_name] = {
                    "exists": True,
                    "file_count": len(files),
                    "files": files[:10] if files else [],
                    "recent_files": sorted(files, reverse=True)[:5] if files else []
                }
                total_files += len(files)
            except Exception as e:
                bucket_status[bucket_name] = {
                    "exists": False,
                    "error": str(e)
                }
        return {
            "total_buckets": len(all_buckets),
            "bucket_status": bucket_status,
            "total_files_across_all_buckets": total_files,
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
