import os
import uuid
import shutil
from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException
from minio import Minio
from minio.error import S3Error
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self):
        self.minio_client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False  # Set to True for HTTPS
        )
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the MinIO bucket exists"""
        try:
            if not self.minio_client.bucket_exists(settings.minio_bucket_name):
                self.minio_client.make_bucket(settings.minio_bucket_name)
                logger.info(f"Created bucket: {settings.minio_bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
    
    def validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        if not file.filename:
            return False
        
        # Check file extension
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in settings.allowed_extensions_list:
            return False
        
        # Check file size (if available)
        if hasattr(file, 'size') and file.size and file.size > settings.max_file_size:
            return False
        
        return True
    
    async def save_file_locally(self, file: UploadFile) -> Tuple[str, str, int]:
        """Save file locally and return file path, filename, and size"""
        if not self.validate_file(file):
            raise HTTPException(status_code=400, detail="Invalid file")
        
        # Generate unique filename
        file_ext = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Ensure upload directory exists
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Save file locally
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                file_size = len(content)
            
            return file_path, unique_filename, file_size
        
        except Exception as e:
            logger.error(f"Error saving file locally: {e}")
            raise HTTPException(status_code=500, detail="Error saving file")
    
    def upload_to_minio(self, local_file_path: str, object_name: str) -> str:
        """Upload file to MinIO and return object path"""
        try:
            self.minio_client.fput_object(
                settings.minio_bucket_name,
                object_name,
                local_file_path
            )
            return f"{settings.minio_bucket_name}/{object_name}"
        
        except S3Error as e:
            logger.error(f"Error uploading to MinIO: {e}")
            raise HTTPException(status_code=500, detail="Error uploading to storage")
    
    def download_from_minio(self, object_name: str, local_file_path: str) -> bool:
        """Download file from MinIO to local path"""
        try:
            self.minio_client.fget_object(
                settings.minio_bucket_name,
                object_name,
                local_file_path
            )
            return True
        
        except S3Error as e:
            logger.error(f"Error downloading from MinIO: {e}")
            return False
    
    def delete_from_minio(self, object_name: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.minio_client.remove_object(settings.minio_bucket_name, object_name)
            return True
        
        except S3Error as e:
            logger.error(f"Error deleting from MinIO: {e}")
            return False
    
    def delete_local_file(self, file_path: str) -> bool:
        """Delete local file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        
        except Exception as e:
            logger.error(f"Error deleting local file: {e}")
            return False
    
    async def process_bulk_upload(self, files: List[UploadFile]) -> Tuple[List[dict], List[dict]]:
        """Process multiple file uploads"""
        successful_uploads = []
        failed_uploads = []
        
        for file in files:
            try:
                if not self.validate_file(file):
                    failed_uploads.append({
                        "filename": file.filename,
                        "error": "Invalid file format or size"
                    })
                    continue
                
                # Save file locally
                file_path, unique_filename, file_size = await self.save_file_locally(file)
                
                # Upload to MinIO
                minio_path = self.upload_to_minio(file_path, unique_filename)
                
                successful_uploads.append({
                    "original_filename": file.filename,
                    "filename": unique_filename,
                    "file_path": file_path,
                    "minio_path": minio_path,
                    "file_size": file_size,
                    "file_type": file.filename.split('.')[-1].lower()
                })
            
            except Exception as e:
                failed_uploads.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return successful_uploads, failed_uploads


# Global file service instance
file_service = FileService()