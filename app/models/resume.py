from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.sql import func
from app.models.database import Base


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    minio_path = Column(String(500), nullable=True)
    
    # Extracted candidate information
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)
    candidate_phone = Column(String(50), nullable=True)
    
    # Resume content
    raw_text = Column(Text, nullable=True)
    processed_text = Column(Text, nullable=True)
    
    # Job role categorization
    job_role = Column(String(100), nullable=True)
    job_role_confidence = Column(Float, nullable=True)
    
    # Skills and experience
    skills = Column(JSON, nullable=True)  # List of extracted skills
    experience_years = Column(Float, nullable=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Vector embedding info
    embedding_id = Column(String(100), nullable=True)  # ID in Qdrant
    embedding_collection = Column(String(100), nullable=True)  # Qdrant collection name
    
    # Metadata
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(10), nullable=True)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processed_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Resume(id={self.id}, filename='{self.filename}', candidate='{self.candidate_name}')>"


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    
    # Job categorization
    job_role = Column(String(100), nullable=False)
    experience_level = Column(String(50), nullable=True)  # junior, mid, senior
    
    # Skills required
    required_skills = Column(JSON, nullable=True)
    preferred_skills = Column(JSON, nullable=True)
    
    # Vector embedding info
    embedding_id = Column(String(100), nullable=True)
    
    # Metadata
    created_by = Column(String(255), nullable=True)
    created_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<JobDescription(id={self.id}, title='{self.title}', role='{self.job_role}')>"


class SearchResult(Base):
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    job_description_id = Column(Integer, nullable=False)
    resume_id = Column(Integer, nullable=False)
    
    # Matching scores
    similarity_score = Column(Float, nullable=False)
    relevance_score = Column(Float, nullable=True)
    
    # Ranking information
    rank_position = Column(Integer, nullable=False)
    
    # LLM explanation (generated on-demand)
    explanation = Column(Text, nullable=True)
    explanation_generated = Column(Boolean, default=False)
    
    # Search metadata
    search_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    search_query_hash = Column(String(64), nullable=True)  # Hash of search parameters
    
    def __repr__(self):
        return f"<SearchResult(job_id={self.job_description_id}, resume_id={self.resume_id}, score={self.similarity_score})>"