from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from .database import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    minio_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)
    
    # Vector database info
    embedding_id = Column(String(100), nullable=True)
    embedding_collection = Column(String(100), nullable=True)
    
    # Job role
    job_role = Column(String(100), nullable=True)
    
    # All fields from vector payload - using exact field names
    name = Column(String(255), nullable=True)
    email_id = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    current_job_title = Column(String(255), nullable=True)
    objective = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)
    qualifications_summary = Column(Text, nullable=True)
    experience_summary = Column(Text, nullable=True)
    companies_worked_with_duration = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    awards_achievements = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)
    availability_status = Column(String(100), nullable=True)
    work_authorization_status = Column(String(100), nullable=True)
    has_photo = Column(Boolean, default=False)
    personal_details = Column(Text, nullable=True)
    personal_info = Column(Text, nullable=True)
    _original_filename = Column(String(255), nullable=True)
    _is_master_record = Column(Boolean, default=True)
    _duplicate_group_id = Column(String(100), nullable=True)
    _duplicate_count = Column(Integer, default=1)
    _associated_original_filenames = Column(JSON, nullable=True)
    _associated_ids = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    job_role = Column(String(100), nullable=True)
    
    # Vector database info
    embedding_id = Column(String(100), nullable=True)
    embedding_collection = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SearchResult(Base):
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    job_role = Column(String(100), nullable=True)
    resume_id = Column(Integer, nullable=False)
    similarity_score = Column(Float, nullable=False)
    rank_position = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())