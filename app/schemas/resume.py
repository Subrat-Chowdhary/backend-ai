from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel


class ResumeBase(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    job_role: Optional[str] = None


class ResumeCreate(ResumeBase):
    pass


class ResumeUpdate(BaseModel):
    job_role: Optional[str] = None
    name: Optional[str] = None
    email_id: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    current_job_title: Optional[str] = None
    skills: Optional[Any] = None
    experience_summary: Optional[str] = None
    qualifications_summary: Optional[str] = None


class Resume(ResumeBase):
    id: int
    minio_path: Optional[str] = None
    is_processed: bool = False
    processing_status: str = "pending"
    error_message: Optional[str] = None
    embedding_id: Optional[str] = None
    embedding_collection: Optional[str] = None
    
    # All fields from vector payload - using exact field names
    name: Optional[str] = None
    email_id: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    location: Optional[str] = None
    current_job_title: Optional[str] = None
    objective: Optional[str] = None
    skills: Optional[Any] = None
    qualifications_summary: Optional[str] = None
    experience_summary: Optional[str] = None
    companies_worked_with_duration: Optional[Any] = None
    certifications: Optional[Any] = None
    awards_achievements: Optional[Any] = None
    projects: Optional[Any] = None
    languages: Optional[Any] = None
    availability_status: Optional[str] = None
    work_authorization_status: Optional[str] = None
    has_photo: Optional[bool] = None
    personal_details: Optional[str] = None
    personal_info: Optional[str] = None
    _original_filename: Optional[str] = None
    _is_master_record: Optional[bool] = None
    _duplicate_group_id: Optional[str] = None
    _duplicate_count: Optional[int] = None
    _associated_original_filenames: Optional[Any] = None
    _associated_ids: Optional[Any] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResumeCardInfo(BaseModel):
    """Resume card info with all fields from vector payload"""
    id: str
    similarity_score: float
    
    # All fields from vector payload - using exact field names
    name: Optional[str] = None
    email_id: Optional[str] = None
    phone_number: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    location: Optional[str] = None
    current_job_title: Optional[str] = None
    objective: Optional[str] = None
    skills: Optional[Any] = None
    qualifications_summary: Optional[str] = None
    experience_summary: Optional[str] = None
    companies_worked_with_duration: Optional[Any] = None
    certifications: Optional[Any] = None
    awards_achievements: Optional[Any] = None
    projects: Optional[Any] = None
    languages: Optional[Any] = None
    availability_status: Optional[str] = None
    work_authorization_status: Optional[str] = None
    has_photo: Optional[bool] = None
    personal_details: Optional[str] = None
    personal_info: Optional[str] = None
    _original_filename: Optional[str] = None
    _is_master_record: Optional[bool] = None
    _duplicate_group_id: Optional[str] = None
    _duplicate_count: Optional[int] = None
    _associated_original_filenames: Optional[Any] = None
    _associated_ids: Optional[Any] = None
    
    # File information
    filename: Optional[str] = None
    minio_path: Optional[str] = None
    upload_timestamp: datetime
    text_preview: Optional[str] = None


class BulkUploadResponse(BaseModel):
    uploaded_files: List[str]
    failed_files: List[str]
    total_uploaded: int
    total_failed: int


class ProcessingStatus(BaseModel):
    resume_id: int
    status: str
    message: Optional[str] = None


class SearchRequest(BaseModel):
    job_description: str
    job_role: Optional[str] = None
    limit: int = 10
    similarity_threshold: float = 0.5


class SearchResultItem(BaseModel):
    resume_id: Any
    resume: Resume
    similarity_score: float
    rank_position: int


class SearchResponse(BaseModel):
    query: SearchRequest
    results: List[SearchResultItem]
    total_results: int
    search_timestamp: datetime