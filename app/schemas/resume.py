from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr


class ResumeBase(BaseModel):
    filename: str
    original_filename: str
    job_role: Optional[str] = None


class ResumeCreate(ResumeBase):
    file_path: str
    file_size: int
    file_type: str


class ResumeUpdate(BaseModel):
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_phone: Optional[str] = None
    raw_text: Optional[str] = None
    processed_text: Optional[str] = None
    job_role: Optional[str] = None
    job_role_confidence: Optional[float] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    is_processed: Optional[bool] = None
    processing_status: Optional[str] = None
    error_message: Optional[str] = None
    embedding_id: Optional[str] = None
    embedding_collection: Optional[str] = None


class Resume(ResumeBase):
    id: int
    file_path: str
    minio_path: Optional[str] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    candidate_phone: Optional[str] = None
    raw_text: Optional[str] = None
    processed_text: Optional[str] = None
    job_role_confidence: Optional[float] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    is_processed: bool
    processing_status: str
    error_message: Optional[str] = None
    embedding_id: Optional[str] = None
    embedding_collection: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    upload_timestamp: datetime
    processed_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobDescriptionBase(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = None
    job_role: str
    experience_level: Optional[str] = None


class JobDescriptionCreate(JobDescriptionBase):
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    created_by: Optional[str] = None


class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    job_role: Optional[str] = None
    experience_level: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    is_active: Optional[bool] = None


class JobDescription(JobDescriptionBase):
    id: int
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    embedding_id: Optional[str] = None
    created_by: Optional[str] = None
    created_timestamp: datetime
    is_active: bool

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    job_description: str
    job_role: Optional[str] = None
    experience_level: Optional[str] = None
    required_skills: Optional[List[str]] = None
    limit: int = 10
    similarity_threshold: float = 0.5


class SearchResultItem(BaseModel):
    resume_id: int
    resume: Resume
    similarity_score: float
    relevance_score: Optional[float] = None
    rank_position: int
    explanation: Optional[str] = None


class SearchResponse(BaseModel):
    query: SearchRequest
    results: List[SearchResultItem]
    total_results: int
    search_timestamp: datetime


class ExplanationRequest(BaseModel):
    job_description_id: int
    resume_id: int


class ExplanationResponse(BaseModel):
    job_description_id: int
    resume_id: int
    explanation: str
    generated_timestamp: datetime


class BulkUploadResponse(BaseModel):
    uploaded_files: List[str]
    failed_files: List[Dict[str, str]]
    total_uploaded: int
    total_failed: int


class ProcessingStatus(BaseModel):
    resume_id: int
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None