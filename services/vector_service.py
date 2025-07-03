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
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = "resumes"
        self.embedding_model = None
    
    async def initialize_collections(self):
        """Initialize Qdrant collections"""
        try:
            # Create collection if it doesn't exist
            async with httpx.AsyncClient() as client:
                # Check if collection exists
                response = await client.get(f"{self.qdrant_url}/collections/{self.collection_name}")
                
                if response.status_code == 404:
                    # Create collection
                    collection_config = {
                        "vectors": {
                            "size": 384,  # all-MiniLM-L6-v2 embedding size
                            "distance": "Cosine"
                        }
                    }
                    
                    response = await client.put(
                        f"{self.qdrant_url}/collections/{self.collection_name}",
                        json=collection_config
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Created Qdrant collection: {self.collection_name}")
                    else:
                        logger.error(f"Failed to create collection: {response.text}")
                else:
                    logger.info(f"Qdrant collection {self.collection_name} already exists")
        
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
                           limit: int = 10, similarity_threshold: float = 0.7) -> List[Dict]:
        """Search for similar resumes"""
        try:
            logger.info(f"Search request: query='{query_text}', category='{job_category}', limit={limit}, threshold={similarity_threshold}")
            
            # Create query embedding
            query_embedding = await self.create_embedding(query_text)
            logger.info(f"Query embedding created, length: {len(query_embedding)}")
            
            # Prepare search request
            search_request = {
                "vector": query_embedding,
                "limit": limit,
                "score_threshold": similarity_threshold
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
            
            # Perform search with payload and vectors
            search_request["with_payload"] = True  # Important: Include payload in response
            search_request["with_vector"] = False  # Don't need vectors in response
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.qdrant_url}/collections/{self.collection_name}/points/search",
                    json=search_request
                )
                
                logger.info(f"Qdrant response status: {response.status_code}")
                logger.info(f"Qdrant response: {response.text}")
                
                if response.status_code == 200:
                    results = response.json()
                    logger.info(f"Raw search results: {results}")
                    
                    # Format results
                    formatted_results = []
                    for result in results.get("result", []):
                        payload = result.get("payload", {})
                        formatted_results.append({
                            "id": result["id"],
                            "similarity_score": result["score"],
                            "filename": payload.get("filename", "Unknown"),
                            "job_category": payload.get("job_category", "Unknown"),
                            "minio_path": payload.get("minio_path", ""),
                            "upload_timestamp": payload.get("upload_timestamp", ""),
                            "text_preview": payload.get("text_content", "")[:200] + "..." if payload.get("text_content") else "No preview available"
                        })
                    
                    logger.info(f"Found {len(formatted_results)} matching resumes")
                    return formatted_results
                else:
                    logger.error(f"Search failed: {response.text}")
                    return []
        
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
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

# Global instance
vector_service = VectorService()