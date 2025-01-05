from typing import Optional
from fastapi import HTTPException

from app.services.llm_service import LLMService

llm_service = LLMService()

async def get_active_llm() -> str:
    """
    Get ID of an active LLM from MongoDB.
    Returns the first active LLM found.
    
    Raises:
        HTTPException: If no active LLM is found
    """
    try:
        active_providers = await llm_service.list_active_providers()
        if not active_providers:
            raise HTTPException(
                status_code=500,
                detail="No active LLM providers found"
            )
        
        # Return the first active provider's ID
        return str(active_providers[0]["_id"])
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active LLM: {str(e)}"
        ) 