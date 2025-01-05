from typing import Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

class SearchQuery(BaseModel):
    """Search query model."""
    query: str
    llm_id: str  # Required LLM ID to use
    top_k: Optional[int] = 5
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

@router.post("/rag-search")
async def rag_search(query: SearchQuery) -> Dict:
    """
    Execute RAG search using the specified LLM.
    
    Args:
        query: Search query parameters including LLM ID
    
    Returns:
        Dict containing answer, relevant documents, and query
    """
    try:
        # Initialize RAG pipeline with specified LLM
        if rag_service.pipeline is None:
            await rag_service.initialize(query.llm_id)
        # If pipeline exists but with different LLM, reinitialize
        elif rag_service.current_llm_id != query.llm_id:
            await rag_service.initialize(query.llm_id)
        
        # Execute search
        result = await rag_service.query(
            query=query.query,
            top_k=query.top_k,
            max_tokens=query.max_tokens,
            temperature=query.temperature
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG search failed: {str(e)}"
        ) 