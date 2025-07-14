"""
MinIO Storage Service for MVP
Handles file uploads and bucket management
"""
import logging
from minio import Minio
from minio.error import S3Error
import io
from typing import Optional

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        import os
        endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
    
    async def bucket_exists(self, bucket_name: str) -> bool:
        """Check if bucket exists"""
        try:
            return self.client.bucket_exists(bucket_name)
        except S3Error as e:
            logger.error(f"Error checking bucket {bucket_name}: {e}")
            return False
    
    async def create_bucket_if_not_exists(self, bucket_name: str) -> bool:
        """Create bucket if it doesn't exist"""
        try:
            if not await self.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"Error creating bucket {bucket_name}: {e}")
            return False
    
    async def upload_file(self, bucket_name: str, object_name: str, file_content: bytes) -> str:
        """Upload file to MinIO"""
        try:
            # Ensure bucket exists
            await self.create_bucket_if_not_exists(bucket_name)
            
            # Upload file
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(file_content),
                length=len(file_content)
            )
            
            minio_path = f"{bucket_name}/{object_name}"
            logger.info(f"Uploaded file to MinIO: {minio_path}")
            return minio_path
        
        except S3Error as e:
            logger.error(f"Error uploading file to MinIO: {e}")
            raise Exception(f"MinIO upload failed: {str(e)}")
    
    async def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(bucket_name, object_name)
            return response.read()
        except S3Error as e:
            logger.error(f"Error downloading file from MinIO: {e}")
            raise Exception(f"MinIO download failed: {str(e)}")
    
    async def list_files(self, bucket_name: str, prefix: Optional[str] = None) -> list:
        """List files in bucket"""
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing files in MinIO: {e}")
            return []
    
    async def list_all_buckets(self) -> list:
        """List all buckets"""
        try:
            buckets = self.client.list_buckets()
            return [bucket.name for bucket in buckets]
        except S3Error as e:
            logger.error(f"Error listing buckets in MinIO: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check MinIO health"""
        try:
            buckets = self.client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}")
            return False

# Global instance
storage_service = StorageService()