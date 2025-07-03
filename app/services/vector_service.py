import uuid
import logging
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from app.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    def __init__(self):
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(url=settings.qdrant_url)
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.embedding_model = None
            self.embedding_dimension = 384  # Default dimension for all-MiniLM-L6-v2
        
        # Initialize collections for different job roles
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize Qdrant collections for each job role"""
        for job_role in settings.job_roles_list:
            collection_name = f"resumes_{job_role.lower()}"
            try:
                # Check if collection exists
                collections = self.qdrant_client.get_collections()
                collection_exists = any(
                    col.name == collection_name 
                    for col in collections.collections
                )
                
                if not collection_exists:
                    # Create collection
                    self.qdrant_client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=self.embedding_dimension,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"Created collection: {collection_name}")
                
            except Exception as e:
                logger.error(f"Error initializing collection {collection_name}: {e}")
        
        # Create general collection for job descriptions
        try:
            collections = self.qdrant_client.get_collections()
            if not any(col.name == "job_descriptions" for col in collections.collections):
                self.qdrant_client.create_collection(
                    collection_name="job_descriptions",
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                logger.info("Created collection: job_descriptions")
        except Exception as e:
            logger.error(f"Error creating job_descriptions collection: {e}")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not self.embedding_model:
            logger.error("Embedding model not available")
            return None
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def add_resume_embedding(
        self, 
        resume_id: int, 
        text: str, 
        job_role: str,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """Add resume embedding to appropriate collection"""
        if not job_role or job_role not in settings.job_roles_list:
            job_role = "General"
        
        collection_name = f"resumes_{job_role.lower()}"
        
        # Generate embedding
        embedding = self.generate_embedding(text)
        if not embedding:
            return None
        
        # Generate unique point ID
        point_id = str(uuid.uuid4())
        
        # Prepare metadata
        payload = {
            "resume_id": resume_id,
            "job_role": job_role,
            "text_preview": text[:200],  # Store preview for debugging
            **(metadata or {})
        }
        
        try:
            # Add point to collection
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            logger.info(f"Added resume {resume_id} to collection {collection_name}")
            return point_id
        
        except Exception as e:
            logger.error(f"Error adding resume embedding: {e}")
            return None
    
    def add_job_description_embedding(
        self, 
        job_description_id: int, 
        text: str,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """Add job description embedding"""
        # Generate embedding
        embedding = self.generate_embedding(text)
        if not embedding:
            return None
        
        # Generate unique point ID
        point_id = str(uuid.uuid4())
        
        # Prepare metadata
        payload = {
            "job_description_id": job_description_id,
            "text_preview": text[:200],
            **(metadata or {})
        }
        
        try:
            # Add point to job descriptions collection
            self.qdrant_client.upsert(
                collection_name="job_descriptions",
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            logger.info(f"Added job description {job_description_id} to collection")
            return point_id
        
        except Exception as e:
            logger.error(f"Error adding job description embedding: {e}")
            return None
    
    def search_similar_resumes(
        self, 
        query_text: str, 
        job_role: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.5
    ) -> List[Dict]:
        """Search for similar resumes"""
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        if not query_embedding:
            return []
        
        results = []
        
        # Determine which collections to search
        collections_to_search = []
        if job_role and job_role in settings.job_roles_list:
            collections_to_search = [f"resumes_{job_role.lower()}"]
        else:
            # Search all resume collections
            collections_to_search = [
                f"resumes_{role.lower()}" for role in settings.job_roles_list
            ]
        
        for collection_name in collections_to_search:
            try:
                # Check if collection exists
                collections = self.qdrant_client.get_collections()
                if not any(col.name == collection_name for col in collections.collections):
                    continue
                
                # Perform search
                search_results = self.qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=query_embedding,
                    limit=limit,
                    score_threshold=score_threshold
                )
                
                # Process results
                for result in search_results:
                    results.append({
                        "resume_id": result.payload["resume_id"],
                        "job_role": result.payload["job_role"],
                        "similarity_score": result.score,
                        "collection": collection_name,
                        "point_id": result.id
                    })
            
            except Exception as e:
                logger.error(f"Error searching collection {collection_name}: {e}")
        
        # Sort by similarity score and return top results
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]
    
    def update_resume_embedding(
        self, 
        point_id: str, 
        collection_name: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Update existing resume embedding"""
        # Generate new embedding
        embedding = self.generate_embedding(text)
        if not embedding:
            return False
        
        try:
            # Get existing point to preserve some metadata
            existing_points = self.qdrant_client.retrieve(
                collection_name=collection_name,
                ids=[point_id]
            )
            
            if not existing_points:
                logger.error(f"Point {point_id} not found in collection {collection_name}")
                return False
            
            existing_payload = existing_points[0].payload
            
            # Update payload with new metadata
            updated_payload = {
                **existing_payload,
                "text_preview": text[:200],
                **(metadata or {})
            }
            
            # Update point
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=updated_payload
                    )
                ]
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating resume embedding: {e}")
            return False
    
    def delete_resume_embedding(self, point_id: str, collection_name: str) -> bool:
        """Delete resume embedding"""
        try:
            self.qdrant_client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=[point_id]
                )
            )
            return True
        
        except Exception as e:
            logger.error(f"Error deleting resume embedding: {e}")
            return False
    
    def delete_job_description_embedding(self, point_id: str) -> bool:
        """Delete job description embedding"""
        try:
            self.qdrant_client.delete(
                collection_name="job_descriptions",
                points_selector=models.PointIdsList(
                    points=[point_id]
                )
            )
            return True
        
        except Exception as e:
            logger.error(f"Error deleting job description embedding: {e}")
            return False
    
    def update_job_description_embedding(
        self, 
        embedding_id: str, 
        text: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Update job description embedding"""
        # Generate new embedding
        embedding = self.generate_embedding(text)
        if not embedding:
            return False
        
        try:
            # Get existing point to preserve some metadata
            existing_points = self.qdrant_client.retrieve(
                collection_name="job_descriptions",
                ids=[embedding_id]
            )
            
            if not existing_points:
                logger.error(f"Point {embedding_id} not found in job_descriptions collection")
                return False
            
            existing_payload = existing_points[0].payload
            
            # Update payload with new metadata
            updated_payload = {
                **existing_payload,
                "text_preview": text[:200],
                **(metadata or {})
            }
            
            # Update point
            self.qdrant_client.upsert(
                collection_name="job_descriptions",
                points=[
                    PointStruct(
                        id=embedding_id,
                        vector=embedding,
                        payload=updated_payload
                    )
                ]
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating job description embedding: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Dict]:
        """Get statistics for all collections"""
        stats = {}
        
        try:
            collections = self.qdrant_client.get_collections()
            
            for collection in collections.collections:
                try:
                    info = self.qdrant_client.get_collection(collection.name)
                    stats[collection.name] = {
                        "points_count": info.points_count,
                        "vectors_count": info.vectors_count,
                        "status": info.status
                    }
                except Exception as e:
                    logger.error(f"Error getting stats for {collection.name}: {e}")
                    stats[collection.name] = {"error": str(e)}
        
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
        
        return stats


# Global vector service instance
vector_service = VectorService()