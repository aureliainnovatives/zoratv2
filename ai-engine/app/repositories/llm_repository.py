import logging
from typing import Optional, Dict, Any
from bson import ObjectId
from ..core.database import MongoDB
from ..models.llm import LLMConfig

logger = logging.getLogger(__name__)

class LLMRepository:
    """Repository for LLM configurations in MongoDB"""
    
    COLLECTION_NAME = "llms"
    
    async def get_by_id(self, llm_id: str) -> Optional[LLMConfig]:
        """Get LLM configuration by ID"""
        try:
            db = MongoDB.get_db()
            if db is None:
                raise RuntimeError("Database connection not initialized")
                
            result = await db[self.COLLECTION_NAME].find_one({"_id": ObjectId(llm_id)})
            
            if result:
                # Convert ObjectId to string for JSON serialization
                result["_id"] = str(result["_id"])
                logger.debug(f"Found LLM configuration: {result}")
                
                # Map MongoDB fields to LLMConfig fields
                return LLMConfig(
                    name=result.get("name", "Unknown"),
                    description=result.get("description", ""),
                    type=result.get("type", "API_BASED"),
                    provider=result.get("provider", "OPENAI"),
                    api_key=result.get("apiKey"),
                    base_url=result.get("baseUrl"),
                    model_name=result.get("modelName", "gpt-3.5-turbo"),
                    is_active=result.get("isActive", True),
                    max_tokens=result.get("maxTokens", 1000),
                    temperature=result.get("temperature", 0.7)
                )
            else:
                logger.warning(f"No LLM found with ID: {llm_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching LLM {llm_id}: {str(e)}")
            raise 