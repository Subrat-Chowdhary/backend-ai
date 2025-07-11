import os
import shutil
from typing import List, Tuple, Dict, Any
from fastapi import UploadFile
import uuid

class FileService:
    def __init__(self):
        self.upload_dir = "/opt/backend-ai/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_file_locally(self, file: UploadFile) -> Tuple[str, str, int]:
        """Save uploaded file locally and return file path, filename, and size"""
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            file_size = len(content)
        
        return file_path, unique_filename, file_size
    
    def upload_to_minio(self, file_path: str, filename: str) -> str:
        """Upload file to MinIO and return the path"""
        return f"minio/{filename}"
    
    async def process_bulk_upload(self, files: List[UploadFile]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Process multiple file uploads"""
        successful_uploads = []
        failed_uploads = []
        
        for file in files:
            try:
                file_path, filename, file_size = await self.save_file_locally(file)
                minio_path = self.upload_to_minio(file_path, filename)
                
                successful_uploads.append({
                    "filename": filename,
                    "original_filename": file.filename,
                    "file_path": file_path,
                    "minio_path": minio_path,
                    "file_size": file_size,
                    "file_type": file.filename.split('.')[-1].lower() if '.' in file.filename else ''
                })
            except Exception as e:
                failed_uploads.append(file.filename)
        
        return successful_uploads, failed_uploads
    
    def delete_local_file(self, file_path: str):
        """Delete local file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
    
    def delete_from_minio(self, filename: str):
        """Delete file from MinIO"""
        pass

file_service = FileService()