"""
Vector Service for MVP
Handles embeddings and vectorized search using Qdrant
"""
import logging
import httpx
import json
import uuid
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        import os
        self.qdrant_url = os.getenv("QDRANT_URL", "http://157.180.44.51:6333")
        self.collection_name = "employee_profiles"
        self.embedding_model = None
    
    async def initialize_collections(self):
        """Initialize Qdrant collections"""
        try:
            # Check if employee_profiles collection exists
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.qdrant_url}/collections/{self.collection_name}")
                
                if response.status_code == 200:
                    logger.info(f"Qdrant collection {self.collection_name} already exists")
                else:
                    logger.info(f"Note: {self.collection_name} collection not found on the server")
                    
                    # We don't create the collection here as it should be pre-created on the server
        
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collections: {e}")
    
    async def get_embedding_model(self):
        """Get or initialize embedding model"""
        if self.embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded embedding model: all-MiniLM-L6-v2")
            except ImportError:
                logger.warning("sentence-transformers not available, using mock embeddings")
                self.embedding_model = "mock"
        
        return self.embedding_model
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        try:
            model = await self.get_embedding_model()
            
            if model == "mock":
                # Mock embedding for testing (384 dimensions)
                import hashlib
                import struct
                
                # Create deterministic mock embedding based on text hash
                text_hash = hashlib.md5(text.encode()).digest()
                embedding = []
                
                for i in range(0, len(text_hash), 4):
                    chunk = text_hash[i:i+4]
                    if len(chunk) == 4:
                        val = struct.unpack('f', chunk)[0]
                        embedding.append(val)
                
                # Pad or truncate to 384 dimensions
                while len(embedding) < 384:
                    embedding.extend(embedding[:min(len(embedding), 384 - len(embedding))])
                
                return embedding[:384]
            else:
                # Real embedding
                embedding = model.encode(text)
                return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * 384
    
    async def add_document(self, text: str, metadata: Dict) -> str:
        """Add document to vector database"""
        try:
            # Create embedding
            embedding = await self.create_embedding(text)
            
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            
            # Prepare point for Qdrant
            point = {
                "id": doc_id,
                "vector": embedding,
                "payload": {
                    **metadata,
                    "text_content": text[:1000],  # Store first 1000 chars
                    "text_length": len(text)
                }
            }
            
            # Insert into Qdrant
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.qdrant_url}/collections/{self.collection_name}/points",
                    json={
                        "points": [point]
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Added document to vector DB: {doc_id}")
                    return doc_id
                else:
                    logger.error(f"Failed to add document to vector DB: {response.text}")
                    raise Exception(f"Vector DB insertion failed: {response.text}")
        
        except Exception as e:
            logger.error(f"Document addition failed: {e}")
            raise Exception(f"Vector DB error: {str(e)}")
    
    async def search_resumes(self, query_text: str, job_category: Optional[str] = None, 
                           limit: int = 10, similarity_threshold: float = 0.7, 
                           enhance_query: bool = True) -> List[Dict]:
        """Search for similar resumes in employee_profiles collection"""
        try:
            logger.info(f"Search request: query='{query_text}', category='{job_category}', limit={limit}, threshold={similarity_threshold}")
            
            # Enhance query if enabled
            final_query = query_text
            if enhance_query:
                try:
                    from .query_enhancer import enhance_search_query
                    context = {"job_category": job_category} if job_category else None
                    final_query = await enhance_search_query(query_text, context)
                    if final_query != query_text:
                        logger.info(f"Query enhanced: '{query_text}' -> '{final_query}'")
                except ImportError:
                    logger.info("Query enhancer not available, using original query")
                except Exception as e:
                    logger.warning(f"Query enhancement failed: {e}, using original query")
            
            # Create query embedding
            query_embedding = await self.create_embedding(final_query)
            logger.info(f"Query embedding created, length: {len(query_embedding)}")
            
            # Prepare search request
            search_request = {
                "vector": query_embedding,
                "limit": limit,
                "score_threshold": similarity_threshold,
                "with_payload": True,  # Include payload in response
                "with_vector": False   # Don't need vectors in response
            }
            
            # Add filter for job category if specified
            if job_category:
                search_request["filter"] = {
                    "must": [
                        {
                            "key": "job_category",
                            "match": {
                                "value": job_category
                            }
                        }
                    ]
                }
            
            logger.info(f"Search request payload: {search_request}")
            
            results = []
            
            # Search in employee_profiles collection
            async with httpx.AsyncClient() as client:
                logger.info(f"Searching in {self.collection_name} collection")
                response = await client.post(
                    f"{self.qdrant_url}/collections/{self.collection_name}/points/search",
                    json=search_request
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"Found {len(response_data.get('result', []))} results in {self.collection_name}")
                    
                    # Format results - using exact field names from Qdrant payload
                    for result in response_data.get("result", []):
                        payload = result.get("payload", {})
                        results.append({
                            "id": result["id"],
                            "similarity_score": result["score"],
                            "collection": self.collection_name,
                            "name": payload.get("name", "Unknown"),
                            "email_id": payload.get("email_id", "Unknown"),
                            "phone_number": payload.get("phone_number", "Unknown"),
                            "location": payload.get("location", "Unknown"),
                            "skills": payload.get("skills", []),
                            "experience_summary": payload.get("experience_summary", ""),
                            "qualifications_summary": payload.get("qualifications_summary", ""),
                            "companies_worked_with_duration": payload.get("companies_worked_with_duration", []),
                            "current_job_title": payload.get("current_job_title", ""),
                            "objective": payload.get("objective", ""),
                            "projects": payload.get("projects", []),
                            "certifications": payload.get("certifications", []),
                            "awards_achievements": payload.get("awards_achievements", []),
                            "languages": payload.get("languages", []),
                            "linkedin_url": payload.get("linkedin_url", "Unknown"),
                            "github_url": payload.get("github_url", "Unknown"),
                            "availability_status": payload.get("availability_status"),
                            "work_authorization_status": payload.get("work_authorization_status"),
                            "has_photo": payload.get("has_photo", False),
                            "_original_filename": payload.get("_original_filename", ""),
                            # Additional fields from Qdrant
                            "personal_details": payload.get("personal_details"),
                            "personal_info": payload.get("personal_info"),
                            "_is_master_record": payload.get("_is_master_record", False),
                            "_duplicate_group_id": payload.get("_duplicate_group_id"),
                            "_duplicate_count": payload.get("_duplicate_count", 0),
                            "_associated_original_filenames": payload.get("_associated_original_filenames", []),
                            "_associated_ids": payload.get("_associated_ids", [])
                        })
                else:
                    logger.error(f"Error searching {self.collection_name}: {response.text}")
            
            logger.info(f"Returning {len(results)} results from {self.collection_name} collection")
            return results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def force_indexing(self) -> bool:
        """Force immediate indexing by updating optimizer config"""
        try:
            async with httpx.AsyncClient() as client:
                # Update collection to force indexing
                update_config = {
                    "optimizer_config": {
                        "indexing_threshold": 0  # Force immediate indexing
                    }
                }
                
                response = await client.patch(
                    f"{self.qdrant_url}/collections/{self.collection_name}",
                    json=update_config
                )
                logger.info(f"Force indexing response: {response.status_code}, {response.text}")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Force indexing failed: {e}")
            return False

    async def rebuild_index(self) -> bool:
        """Rebuild Qdrant index"""
        try:
            async with httpx.AsyncClient() as client:
                # Force index rebuild
                response = await client.post(
                    f"{self.qdrant_url}/collections/{self.collection_name}/index",
                    json={"wait": True}
                )
                logger.info(f"Index rebuild response: {response.status_code}")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Index rebuild failed: {e}")
            return False
    
    async def get_collection_info(self) -> dict:
        """Get collection information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.qdrant_url}/collections/{self.collection_name}")
                if response.status_code == 200:
                    info = response.json()
                    logger.info(f"Collection info: {info}")
                    return info
                return {}
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}

    async def health_check(self) -> bool:
        """Check Qdrant health"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.qdrant_url}/collections")
                if response.status_code == 200:
                    # Log available collections
                    collections = response.json()
                    collection_names = [col["name"] for col in collections.get("result", {}).get("collections", [])]
                    logger.info(f"Available Qdrant collections: {collection_names}")
                    
                    # Check if our collection exists
                    if self.collection_name in collection_names:
                        logger.info(f"Collection {self.collection_name} is available")
                    else:
                        logger.warning(f"Collection {self.collection_name} is NOT available")
                        
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
    
    def search_similar_resumes(self, query_text: str, job_role: Optional[str] = None, 
                              limit: int = 10, score_threshold: float = 0.7) -> List[Dict]:
        """Synchronous wrapper for search_resumes method"""
        try:
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async search method
            results = loop.run_until_complete(
                self.search_resumes(
                    query_text=query_text,
                    job_category=job_role,
                    limit=limit,
                    similarity_threshold=score_threshold
                )
            )
            
            # Map the results to the expected format
            mapped_results = []
            for result in results:
                mapped_result = {
                    "resume_id": result["id"],
                    "similarity_score": result["similarity_score"],
                    "collection": result["collection"],
                    "name": result["name"],
                    "email": result["email"],
                    "phone": result["phone"],
                    "location": result["location"],
                    "skills": result["skills"],
                    "experience": result["experience"],
                    "education": result["education"],
                    "companies": result["companies"],
                    "current_job_title": result.get("current_job_title", ""),
                    "objective": result.get("objective", ""),
                    "projects": result.get("projects", []),
                    "certifications": result.get("certifications", []),
                    "awards_achievements": result.get("awards_achievements", []),
                    "languages": result.get("languages", []),
                    "linkedin_url": result.get("linkedin_url", ""),
                    "github_url": result.get("github_url", ""),
                    "availability_status": result.get("availability_status", ""),
                    "work_authorization_status": result.get("work_authorization_status", ""),
                    "has_photo": result.get("has_photo", False),
                    "_original_filename": result.get("_original_filename", "")
                }
                mapped_results.append(mapped_result)
            
            return mapped_results
        except Exception as e:
            logger.error(f"Search similar resumes failed: {e}")
            return []

# Global instance
vector_service = VectorService()