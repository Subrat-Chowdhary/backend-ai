"""
Query Enhancement Management API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

# Import our modular enhancement service
try:
    from services.query_enhancer import (
        EnhancementStrategy, 
        configure_enhancement, 
        get_enhancement_strategy,
        enhance_search_query
    )
    ENHANCEMENT_AVAILABLE = True
except ImportError:
    ENHANCEMENT_AVAILABLE = False

router = APIRouter(prefix="/enhancement", tags=["Query Enhancement"])


class QueryEnhanceRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None


class QueryEnhanceResponse(BaseModel):
    original_query: str
    enhanced_query: str
    strategy_used: str
    enhancement_applied: bool


class StrategyConfigRequest(BaseModel):
    strategy: str  # none, openai, anthropic, local_llm, custom_api


class StrategyStatusResponse(BaseModel):
    current_strategy: str
    available_strategies: list
    enhancement_enabled: bool


@router.get("/status", response_model=StrategyStatusResponse)
async def get_enhancement_status():
    """Get current query enhancement configuration"""
    if not ENHANCEMENT_AVAILABLE:
        return StrategyStatusResponse(
            current_strategy="unavailable",
            available_strategies=[],
            enhancement_enabled=False
        )
    
    current = get_enhancement_strategy()
    available = [strategy.value for strategy in EnhancementStrategy]
    
    return StrategyStatusResponse(
        current_strategy=current.value,
        available_strategies=available,
        enhancement_enabled=current != EnhancementStrategy.NONE
    )


@router.post("/configure")
async def configure_enhancement_strategy(request: StrategyConfigRequest):
    """Configure query enhancement strategy"""
    if not ENHANCEMENT_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Query enhancement service not available"
        )
    
    try:
        strategy = EnhancementStrategy(request.strategy)
        configure_enhancement(strategy)
        
        return {
            "message": f"Enhancement strategy configured to: {strategy.value}",
            "strategy": strategy.value,
            "success": True
        }
    except ValueError:
        available = [s.value for s in EnhancementStrategy]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Available: {available}"
        )


@router.post("/enhance", response_model=QueryEnhanceResponse)
async def enhance_query_endpoint(request: QueryEnhanceRequest):
    """Enhance a search query using the configured strategy"""
    if not ENHANCEMENT_AVAILABLE:
        return QueryEnhanceResponse(
            original_query=request.query,
            enhanced_query=request.query,
            strategy_used="unavailable",
            enhancement_applied=False
        )
    
    try:
        current_strategy = get_enhancement_strategy()
        enhanced_query = await enhance_search_query(request.query, request.context)
        
        return QueryEnhanceResponse(
            original_query=request.query,
            enhanced_query=enhanced_query,
            strategy_used=current_strategy.value,
            enhancement_applied=enhanced_query != request.query
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query enhancement failed: {str(e)}"
        )


@router.get("/test/{strategy}")
async def test_enhancement_strategy(strategy: str, query: str = "Python developer with 5 years experience"):
    """Test a specific enhancement strategy with a sample query"""
    if not ENHANCEMENT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Query enhancement service not available"
        )
    
    try:
        # Temporarily switch to test strategy
        original_strategy = get_enhancement_strategy()
        test_strategy = EnhancementStrategy(strategy)
        
        configure_enhancement(test_strategy)
        enhanced_query = await enhance_search_query(query)
        
        # Restore original strategy
        configure_enhancement(original_strategy)
        
        return {
            "test_strategy": strategy,
            "original_query": query,
            "enhanced_query": enhanced_query,
            "enhancement_applied": enhanced_query != query,
            "restored_strategy": original_strategy.value
        }
    except ValueError:
        available = [s.value for s in EnhancementStrategy]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Available: {available}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )


@router.get("/strategies")
async def list_available_strategies():
    """List all available enhancement strategies with descriptions"""
    strategies = {
        "none": {
            "description": "No enhancement - returns original query",
            "requirements": "None",
            "performance": "Instant"
        },
        "openai": {
            "description": "OpenAI GPT-based query enhancement",
            "requirements": "OPENAI_API_KEY environment variable",
            "performance": "~1-2 seconds per query"
        },
        "anthropic": {
            "description": "Anthropic Claude-based query enhancement",
            "requirements": "ANTHROPIC_API_KEY environment variable",
            "performance": "~1-2 seconds per query"
        },
        "local_llm": {
            "description": "Local LLM model (requires heavy dependencies)",
            "requirements": "sentence-transformers package installed",
            "performance": "~2-5 seconds per query (first time slower)"
        },
        "custom_api": {
            "description": "Custom API endpoint for enhancement",
            "requirements": "CUSTOM_ENHANCER_URL environment variable",
            "performance": "Depends on your API"
        }
    }
    
    return {
        "available_strategies": strategies,
        "current_strategy": get_enhancement_strategy().value if ENHANCEMENT_AVAILABLE else "unavailable",
        "enhancement_service_available": ENHANCEMENT_AVAILABLE
    }