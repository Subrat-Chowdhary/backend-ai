"""
MinIO Storage Service for MVP
Handles file uploads, bucket management, and model loading/saving.
"""
import asyncio
import logging
from minio import Minio
from minio.error import S3Error
import io
import os
import pickle
import json
from typing import Optional, Tuple, Any, Dict

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        # Corrected MINIO_ENDPOINT IP address
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        # Ensure this line is present and correctly sets the 'secure' attribute
        self.secure = os.getenv("MINIO_SECURE", "False").lower() == "true" # Convert string to boolean

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure # This uses the 'secure' attribute defined above
        )
        logger.info(f"MinIO client initialized for endpoint: {self.endpoint}")

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
            logger.error(f"Error uploading file to MinIO: {e}", exc_info=True)
            raise Exception(f"MinIO upload failed: {str(e)}")
    
    async def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(bucket_name, object_name)
            return response.read()
        except S3Error as e:
            logger.error(f"Error downloading file from MinIO: {e}", exc_info=True)
            raise Exception(f"MinIO download failed: {str(e)}")
    
    async def list_files(self, bucket_name: str, prefix: Optional[str] = None) -> list:
        """List files in bucket"""
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"Error listing files in MinIO: {e}", exc_info=True)
            return []
    
    async def list_all_buckets(self) -> list:
        """List all buckets"""
        try:
            buckets = self.client.list_buckets()
            return [bucket.name for bucket in buckets]
        except S3Error as e:
            logger.error(f"Error listing buckets in MinIO: {e}", exc_info=True)
            return []
    
    async def health_check(self) -> bool:
        """Check MinIO health"""
        try:
            buckets = await asyncio.to_thread(self.client.list_buckets)
            return True
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}", exc_info=True)
            return False

    async def load_sparse_models(self, bucket_name: str, bm25_object_name: str, vocab_object_name: str) -> Tuple[Any, Dict]:
        """
        Loads the persisted BM25 model and token_to_index (vocabulary) from MinIO.
        Returns a tuple: (bm25_model, token_to_index).
        """
        try:
            logger.info(f"Downloading BM25 model from '{bucket_name}/{bm25_object_name}'...")
            bm25_model_bytes = await self.download_file(bucket_name, bm25_object_name)
            bm25_model = pickle.loads(bm25_model_bytes)
            logger.info(f"✅ BM25 model loaded.")

            logger.info(f"Downloading token_to_index from '{bucket_name}/{vocab_object_name}'...")
            token_to_index_bytes = await self.download_file(bucket_name, vocab_object_name)
            token_to_index = json.loads(token_to_index_bytes.decode('utf-8'))
            logger.info(f"✅ token_to_index loaded.")

            return bm25_model, token_to_index

        except S3Error as e:
            logger.error(f"❌ MinIO S3 Error during model loading: {e}", exc_info=True)
            raise Exception(f"Failed to load sparse models from MinIO (S3 Error): {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected error loading sparse models: {e}", exc_info=True)
            raise Exception(f"Failed to load sparse models from MinIO: {str(e)}")


# Global instance
storage_service = StorageService()
