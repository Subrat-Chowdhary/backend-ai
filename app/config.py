import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/resume_db"
    
    # Redis
    redis_url: str = "redis://157.180.44.51:6379/0"
    
    # Qdrant Vector Database
    qdrant_url: str = "http://157.180.44.51:6333"
    
    # MinIO Object Storage
    minio_endpoint: str = "157.180.44.51:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "resumes"
    
    # Application Settings
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: str = "pdf,docx,doc"
    
    # ML Models
    embedding_model: str = "all-MiniLM-L6-v2"
    ner_model: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    
    # Job Role Categories
    job_roles: str = "Backend,Frontend,Database,QA,Fullstack,DevOps,Mobile,DataScience"
    
    class Config:
        env_file = ".env"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    @property
    def job_roles_list(self) -> List[str]:
        return [role.strip() for role in self.job_roles.split(",")]


settings = Settings()