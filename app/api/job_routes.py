from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.resume import JobDescription
from app.schemas.resume import (
    JobDescription as JobDescriptionSchema,
    JobDescriptionCreate,
    JobDescriptionUpdate
)
from app.services.vector_service import vector_service

router = APIRouter(prefix="/jobs", tags=["job-descriptions"])


@router.post("/", response_model=JobDescriptionSchema)
def create_job_description(
    job_data: JobDescriptionCreate,
    db: Session = Depends(get_db)
):
    """Create a new job description"""
    try:
        # Create job description
        job_description = JobDescription(**job_data.dict())
        db.add(job_description)
        db.commit()
        db.refresh(job_description)
        
        # Generate and store embedding
        full_text = f"{job_description.title}\n{job_description.description}"
        if job_description.requirements:
            full_text += f"\n{job_description.requirements}"
        
        embedding_id = vector_service.add_job_description_embedding(
            job_description_id=job_description.id,
            text=full_text,
            metadata={
                "title": job_description.title,
                "job_role": job_description.job_role,
                "experience_level": job_description.experience_level,
                "required_skills": job_description.required_skills,
                "preferred_skills": job_description.preferred_skills
            }
        )
        
        if embedding_id:
            job_description.embedding_id = embedding_id
            db.commit()
            db.refresh(job_description)
        
        return job_description
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[JobDescriptionSchema])
def get_job_descriptions(
    skip: int = 0,
    limit: int = 100,
    job_role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of job descriptions with optional filters"""
    query = db.query(JobDescription)
    
    if job_role:
        query = query.filter(JobDescription.job_role == job_role)
    
    if is_active is not None:
        query = query.filter(JobDescription.is_active == is_active)
    
    job_descriptions = query.offset(skip).limit(limit).all()
    return job_descriptions


@router.get("/{job_id}", response_model=JobDescriptionSchema)
def get_job_description(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job description"""
    job_description = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job_description:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job_description


@router.put("/{job_id}", response_model=JobDescriptionSchema)
def update_job_description(
    job_id: int,
    job_update: JobDescriptionUpdate,
    db: Session = Depends(get_db)
):
    """Update job description"""
    job_description = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job_description:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Update fields
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_description, field, value)
    
    db.commit()
    db.refresh(job_description)
    
    # Update embedding if content changed
    content_fields = ["title", "description", "requirements", "required_skills", "preferred_skills"]
    if any(field in update_data for field in content_fields):
        full_text = f"{job_description.title}\n{job_description.description}"
        if job_description.requirements:
            full_text += f"\n{job_description.requirements}"
        
        if job_description.embedding_id:
            # Update existing embedding
            vector_service.update_job_description_embedding(
                embedding_id=job_description.embedding_id,
                text=full_text,
                metadata={
                    "title": job_description.title,
                    "job_role": job_description.job_role,
                    "experience_level": job_description.experience_level,
                    "required_skills": job_description.required_skills,
                    "preferred_skills": job_description.preferred_skills
                }
            )
        else:
            # Create new embedding
            embedding_id = vector_service.add_job_description_embedding(
                job_description_id=job_description.id,
                text=full_text,
                metadata={
                    "title": job_description.title,
                    "job_role": job_description.job_role,
                    "experience_level": job_description.experience_level,
                    "required_skills": job_description.required_skills,
                    "preferred_skills": job_description.preferred_skills
                }
            )
            
            if embedding_id:
                job_description.embedding_id = embedding_id
                db.commit()
                db.refresh(job_description)
    
    return job_description


@router.delete("/{job_id}")
def delete_job_description(job_id: int, db: Session = Depends(get_db)):
    """Delete a job description"""
    job_description = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job_description:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Delete from vector database if exists
    if job_description.embedding_id:
        vector_service.delete_job_description_embedding(job_description.embedding_id)
    
    # Delete from database
    db.delete(job_description)
    db.commit()
    
    return {"message": "Job description deleted successfully"}


@router.post("/{job_id}/deactivate")
def deactivate_job_description(job_id: int, db: Session = Depends(get_db)):
    """Deactivate a job description"""
    job_description = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job_description:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    job_description.is_active = False
    db.commit()
    
    return {"message": "Job description deactivated successfully"}


@router.post("/{job_id}/activate")
def activate_job_description(job_id: int, db: Session = Depends(get_db)):
    """Activate a job description"""
    job_description = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job_description:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    job_description.is_active = True
    db.commit()
    
    return {"message": "Job description activated successfully"}