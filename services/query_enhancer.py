"""
Modular Query Enhancement Service
Supports multiple enhancement strategies with easy switching
"""
import httpx
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
import os


class EnhancementStrategy(Enum):
    NONE = "none"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL_LLM = "local_llm"
    CUSTOM_API = "custom_api"


class QueryEnhancer(ABC):
    """Abstract base class for query enhancement strategies"""
    
    @abstractmethod
    async def enhance_query(self, original_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Enhance the search query for better vector search results"""
        pass


class NoEnhancement(QueryEnhancer):
    """Pass-through enhancer - returns original query"""
    
    async def enhance_query(self, original_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        return original_query


class OpenAIEnhancer(QueryEnhancer):
    """OpenAI-based query enhancement"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def enhance_query(self, original_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_key:
            return original_query
        
        prompt = self._build_enhancement_prompt(original_query, context)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 150,
                        "temperature": 0.3
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    enhanced_query = result["choices"][0]["message"]["content"].strip()
                    return enhanced_query
                else:
                    print(f"OpenAI API error: {response.status_code}")
                    return original_query
                    
        except Exception as e:
            print(f"Query enhancement failed: {e}")
            return original_query
    
    def _build_enhancement_prompt(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        return f"""
You are a resume search expert. Enhance the following search query to improve vector search results for finding relevant resumes.

Original query: "{query}"

Guidelines:
1. Expand abbreviations and acronyms
2. Add relevant synonyms and related terms
3. Include both technical and soft skills variations
4. Keep it concise but comprehensive
5. Focus on searchable keywords

Return only the enhanced query, no explanations.

Enhanced query:"""


class AnthropicEnhancer(QueryEnhancer):
    """Anthropic Claude-based query enhancement"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    async def enhance_query(self, original_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_key:
            return original_query
        
        # Similar implementation to OpenAI but with Claude API
        # Implementation details would go here
        return original_query  # Placeholder


class CustomAPIEnhancer(QueryEnhancer):
    """Custom API endpoint for query enhancement"""
    
    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or os.getenv("CUSTOM_ENHANCER_URL")
    
    async def enhance_query(self, original_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        if not self.api_url:
            return original_query
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "query": original_query,
                        "context": context or {}
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("enhanced_query", original_query)
                else:
                    return original_query
                    
        except Exception as e:
            print(f"Custom API enhancement failed: {e}")
            return original_query


class LocalLLMEnhancer(QueryEnhancer):
    """Local LLM-based enhancement (requires heavy dependencies)"""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load local model only if dependencies are available"""
        try:
            # This would only work if sentence-transformers is installed
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            print("Local LLM dependencies not available. Install sentence-transformers for local enhancement.")
            self.model = None
    
    async def enhance_query(self, original_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        if not self.model:
            return original_query
        
        # Local enhancement logic would go here
        # For now, return original query
        return original_query


class QueryEnhancementService:
    """Main service that manages different enhancement strategies"""
    
    def __init__(self, strategy: EnhancementStrategy = EnhancementStrategy.NONE):
        self.strategy = strategy
        self.enhancer = self._create_enhancer(strategy)
    
    def _create_enhancer(self, strategy: EnhancementStrategy) -> QueryEnhancer:
        """Factory method to create appropriate enhancer"""
        enhancer_map = {
            EnhancementStrategy.NONE: NoEnhancement,
            EnhancementStrategy.OPENAI: OpenAIEnhancer,
            EnhancementStrategy.ANTHROPIC: AnthropicEnhancer,
            EnhancementStrategy.LOCAL_LLM: LocalLLMEnhancer,
            EnhancementStrategy.CUSTOM_API: CustomAPIEnhancer,
        }
        
        enhancer_class = enhancer_map.get(strategy, NoEnhancement)
        return enhancer_class()
    
    async def enhance_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Enhance query using the configured strategy"""
        return await self.enhancer.enhance_query(query, context)
    
    def switch_strategy(self, new_strategy: EnhancementStrategy):
        """Switch to a different enhancement strategy at runtime"""
        self.strategy = new_strategy
        self.enhancer = self._create_enhancer(new_strategy)
    
    def get_current_strategy(self) -> EnhancementStrategy:
        """Get the currently active strategy"""
        return self.strategy


# Global service instance
query_enhancement_service = QueryEnhancementService()


# Convenience functions
async def enhance_search_query(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Convenience function to enhance a search query"""
    return await query_enhancement_service.enhance_query(query, context)


def configure_enhancement(strategy: EnhancementStrategy):
    """Configure the global enhancement strategy"""
    query_enhancement_service.switch_strategy(strategy)


def get_enhancement_strategy() -> EnhancementStrategy:
    """Get current enhancement strategy"""
    return query_enhancement_service.get_current_strategy()