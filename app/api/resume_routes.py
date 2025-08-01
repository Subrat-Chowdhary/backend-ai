from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from celery.result import AsyncResult

from app.models.database import get_db
from app.models.resume import Resume, JobDescription, SearchResult
from app.schemas.resume import (
    Resume as ResumeSchema,
    ResumeCreate,
    ResumeUpdate,
    BulkUploadResponse,
    ProcessingStatus,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    ResumeCardInfo
)
from app.services.file_service import file_service
from app.services.vector_service import vector_service
from app.tasks.resume_processing import process_resume_task, batch_process_resumes_task
from app.celery_app import celery_app

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeSchema)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_role: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a single resume"""
    try:
        # Save file locally and to MinIO
        file_path, filename, file_size = await file_service.save_file_locally(file)
        minio_path = file_service.upload_to_minio(file_path, filename)
        
        # Create resume record
        resume_data = ResumeCreate(
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file.filename.split('.')[-1].lower()
        )
        
        resume = Resume(
            **resume_data.dict(),
            minio_path=minio_path,
            job_role=job_role
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Start background processing
        background_tasks.add_task(
            lambda: process_resume_task.delay(resume.id)
        )
        
        return resume
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/bulk", response_model=BulkUploadResponse)
async def upload_bulk_resumes(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    job_role: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload multiple resumes"""
    try:
        # Process file uploads
        successful_uploads, failed_uploads = await file_service.process_bulk_upload(files)
        
        resume_ids = []
        uploaded_files = []
        
        # Create resume records for successful uploads
        for upload_info in successful_uploads:
            resume = Resume(
                filename=upload_info["filename"],
                original_filename=upload_info["original_filename"],
                file_path=upload_info["file_path"],
                minio_path=upload_info["minio_path"],
                file_size=upload_info["file_size"],
                file_type=upload_info["file_type"],
                job_role=job_role
            )
            
            db.add(resume)
            db.commit()
            db.refresh(resume)
            
            resume_ids.append(resume.id)
            uploaded_files.append(upload_info["original_filename"])
        
        # Start batch processing
        if resume_ids:
            background_tasks.add_task(
                lambda: batch_process_resumes_task.delay(resume_ids)
            )
        
        return BulkUploadResponse(
            uploaded_files=uploaded_files,
            failed_files=failed_uploads,
            total_uploaded=len(uploaded_files),
            total_failed=len(failed_uploads)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ResumeSchema])
def get_resumes(
    skip: int = 0,
    limit: int = 100,
    job_role: Optional[str] = None,
    is_processed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of resumes with optional filters"""
    query = db.query(Resume)
    
    if job_role:
        query = query.filter(Resume.job_role == job_role)
    
    if is_processed is not None:
        query = query.filter(Resume.is_processed == is_processed)
    
    resumes = query.offset(skip).limit(limit).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeSchema)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Get a specific resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.put("/{resume_id}", response_model=ResumeSchema)
def update_resume(
    resume_id: int,
    resume_update: ResumeUpdate,
    db: Session = Depends(get_db)
):
    """Update resume information"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Update fields
    for field, value in resume_update.dict(exclude_unset=True).items():
        setattr(resume, field, value)
    
    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """Delete a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete from vector database if exists
    if resume.embedding_id and resume.embedding_collection:
        vector_service.delete_resume_embedding(
            resume.embedding_id,
            resume.embedding_collection
        )
    
    # Delete files
    file_service.delete_local_file(resume.file_path)
    if resume.minio_path:
        file_service.delete_from_minio(resume.filename)
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}


@router.post("/{resume_id}/reprocess")
def reprocess_resume(
    resume_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reprocess a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Reset processing status
    resume.is_processed = False
    resume.processing_status = "pending"
    resume.error_message = None
    db.commit()
    
    # Start processing
    task = process_resume_task.delay(resume_id)
    
    return {
        "message": "Resume reprocessing started",
        "task_id": task.id
    }


@router.get("/{resume_id}/status", response_model=ProcessingStatus)
def get_processing_status(resume_id: int, db: Session = Depends(get_db)):
    """Get processing status of a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return ProcessingStatus(
        resume_id=resume_id,
        status=resume.processing_status,
        message=resume.error_message
    )


@router.get("/task/{task_id}/status")
def get_task_status(task_id: str):
    """Get Celery task status"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == "PENDING":
            response = {
                "state": result.state,
                "progress": 0,
                "message": "Task is waiting to be processed"
            }
        elif result.state == "PROCESSING":
            response = {
                "state": result.state,
                **result.info
            }
        elif result.state == "SUCCESS":
            response = {
                "state": result.state,
                "progress": 100,
                "result": result.result
            }
        else:  # FAILURE
            response = {
                "state": result.state,
                "progress": 0,
                "error": str(result.info)
            }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
def search_resumes(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search for matching resumes"""
    try:
        # Perform vector search
        search_results = vector_service.search_similar_resumes(
            query_text=search_request.job_description,
            job_role=search_request.job_role,
            limit=search_request.limit,
            score_threshold=search_request.similarity_threshold
        )
        
        # Get resume details from database or create from employee_profiles data
        result_items = []
        for i, result in enumerate(search_results):
            # Check if this is from employee_profiles collection
            if result.get("collection") == "employee_profiles" and "name" in result:
                # Create a Resume object from employee_profiles data using exact field names
                resume_data = {
                    "id": result.get("id"),
                    "name": result.get("name"),
                    "email_id": result.get("email_id"),
                    "phone_number": result.get("phone_number"),
                    "linkedin_url": result.get("linkedin_url"),
                    "github_url": result.get("github_url"),
                    "location": result.get("location"),
                    "current_job_title": result.get("current_job_title"),
                    "objective": result.get("objective"),
                    "skills": result.get("skills"),
                    "qualifications_summary": result.get("qualifications_summary"),
                    "experience_summary": result.get("experience_summary"),
                    "companies_worked_with_duration": result.get("companies_worked_with_duration"),
                    "certifications": result.get("certifications"),
                    "awards_achievements": result.get("awards_achievements"),
                    "projects": result.get("projects"),
                    "languages": result.get("languages"),
                    "availability_status": result.get("availability_status"),
                    "work_authorization_status": result.get("work_authorization_status"),
                    "has_photo": result.get("has_photo"),
                    "_original_filename": result.get("_original_filename"),
                    "personal_details": result.get("personal_details"),
                    "personal_info": result.get("personal_info"),
                    "_is_master_record": result.get("_is_master_record"),
                    "_duplicate_group_id": result.get("_duplicate_group_id"),
                    "_duplicate_count": result.get("_duplicate_count"),
                    "_associated_original_filenames": result.get("_associated_original_filenames"),
                    "_associated_ids": result.get("_associated_ids"),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Create a Resume object (without saving to DB)
                temp_resume = Resume(**resume_data)
                
                result_items.append(SearchResultItem(
                    resume_id=result.get("id"),
                    resume=temp_resume,
                    similarity_score=result["similarity_score"],
                    rank_position=i + 1
                ))
            else:
                # Traditional resume lookup from database
                resume = db.query(Resume).filter(Resume.id == result["resume_id"]).first()
                if resume:
                    result_items.append(SearchResultItem(
                        resume_id=resume.id,
                        resume=resume,
                        similarity_score=result["similarity_score"],
                        rank_position=i + 1
                    ))
        
        return SearchResponse(
            query=search_request,
            results=result_items,
            total_results=len(result_items),
            search_timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/cards", response_model=List[ResumeCardInfo])
def search_resumes_for_cards(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search for matching resumes and return card-friendly format"""
    try:
        # Perform vector search
        search_results = vector_service.search_similar_resumes(
            query_text=search_request.job_description,
            job_role=search_request.job_role,
            limit=search_request.limit,
            score_threshold=search_request.similarity_threshold
        )
        
        # Get resume details from database and format for cards
        card_results = []
        for result in search_results:
            # Check if this is from employee_profiles collection
            if result.get("collection") == "employee_profiles" and "name" in result:
                # Extract first and last name
                name_parts = result.get("name", "Unknown").split(" ", 1)
                first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
                last_name = name_parts[1] if len(name_parts) > 1 else ""
                
                # Create card directly from employee_profiles data using exact field names
                card_info = ResumeCardInfo(
                    id=str(result.get("id")),
                    similarity_score=result["similarity_score"],
                    name=result.get("name"),
                    email_id=result.get("email_id"),
                    phone_number=result.get("phone_number"),
                    linkedin_url=result.get("linkedin_url"),
                    github_url=result.get("github_url"),
                    location=result.get("location"),
                    current_job_title=result.get("current_job_title"),
                    objective=result.get("objective"),
                    skills=result.get("skills"),
                    qualifications_summary=result.get("qualifications_summary"),
                    experience_summary=result.get("experience_summary"),
                    companies_worked_with_duration=result.get("companies_worked_with_duration"),
                    certifications=result.get("certifications"),
                    awards_achievements=result.get("awards_achievements"),
                    projects=result.get("projects"),
                    languages=result.get("languages"),
                    availability_status=result.get("availability_status"),
                    work_authorization_status=result.get("work_authorization_status"),
                    has_photo=result.get("has_photo"),
                    _original_filename=result.get("_original_filename"),
                    personal_details=result.get("personal_details"),
                    personal_info=result.get("personal_info"),
                    _is_master_record=result.get("_is_master_record"),
                    _duplicate_group_id=result.get("_duplicate_group_id"),
                    _duplicate_count=result.get("_duplicate_count"),
                    _associated_original_filenames=result.get("_associated_original_filenames"),
                    _associated_ids=result.get("_associated_ids"),
                    filename=result.get("_original_filename"),
                    minio_path="",
                    upload_timestamp=datetime.utcnow(),
                    text_preview=result.get("objective")
                )
                card_results.append(card_info)
            else:
                # Traditional resume lookup from database
                resume = db.query(Resume).filter(Resume.id == result["resume_id"]).first()
                if resume:
                    # Create card-friendly response
                    card_info = ResumeCardInfo(
                        id=str(resume.id),
                        similarity_score=result["similarity_score"],
                        first_name=resume.candidate_first_name,
                        last_name=resume.candidate_last_name,
                        full_name=resume.candidate_name,
                        location=resume.candidate_location,
                        total_experience=resume.total_experience,
                        current_ctc=resume.current_ctc,
                        notice_period=resume.notice_period,
                        job_category=resume.job_role,
                        skills=resume.skills,
                        filename=resume.filename,
                        minio_path=resume.minio_path,
                        upload_timestamp=resume.upload_timestamp,
                        text_preview=resume.processed_text[:200] if resume.processed_text else None
                    )
                    card_results.append(card_info)
        
        return card_results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
def get_resume_stats(db: Session = Depends(get_db)):
    """Get resume statistics"""
    try:
        total_resumes = db.query(Resume).count()
        processed_resumes = db.query(Resume).filter(Resume.is_processed == True).count()
        pending_resumes = db.query(Resume).filter(Resume.processing_status == "pending").count()
        failed_resumes = db.query(Resume).filter(Resume.processing_status == "failed").count()
        
        # Get stats by job role
        job_role_stats = {}
        for job_role in ["Backend", "Frontend", "Fullstack", "DevOps", "QA", "Database", "Mobile", "DataScience"]:
            count = db.query(Resume).filter(Resume.job_role == job_role).count()
            if count > 0:
                job_role_stats[job_role] = count
        
        # Get vector database stats
        vector_stats = vector_service.get_collection_stats()
        
        return {
            "total_resumes": total_resumes,
            "processed_resumes": processed_resumes,
            "pending_resumes": pending_resumes,
            "failed_resumes": failed_resumes,
            "processing_rate": round(processed_resumes / total_resumes * 100, 2) if total_resumes > 0 else 0,
            "job_role_distribution": job_role_stats,
            "vector_database_stats": vector_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))