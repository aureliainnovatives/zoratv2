from typing import Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.enhanced_rag_service import EnhancedRAGService

router = APIRouter()
rag_service = EnhancedRAGService()

class SearchQuery(BaseModel):
    """Search query model."""
    query: str
    llm_id: str  # Required LLM ID to use
    top_k: Optional[int] = 5
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    search_type: Optional[str] = "hybrid"  # 'hybrid', 'semantic', or 'keyword'

@router.post("/rag")
async def rag_search(query: SearchQuery) -> Dict:
    """
    Execute enhanced RAG search using the specified LLM.
    
    Args:
        query: Search query parameters including LLM ID and search type
    
    Returns:
        Dict containing answer, relevant documents, and query metadata
    """
    try:
        # Initialize RAG components with specified LLM if not initialized
        # or if LLM has changed
        if rag_service.pipeline is None or rag_service.current_llm_id != query.llm_id:
            await rag_service.initialize(query.llm_id)
        
        # Execute search with parameters
        result = await rag_service.query(
            query=query.query,
            top_k=query.top_k,
            max_tokens=query.max_tokens,
            temperature=query.temperature,
            search_type=query.search_type
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Enhanced RAG search failed: {str(e)}"
        ) 