import logging
from typing import Optional, Dict, Any
from bson import ObjectId
from ..core.database import MongoDB

logger = logging.getLogger(__name__)

class AgentRepository:
    """Repository for agent configurations in MongoDB"""
    
    COLLECTION_NAME = "agents"
    
    async def get_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent configuration by ID"""
        try:
            db = MongoDB.get_db()
            if db is None:
                raise RuntimeError("Database connection not initialized")
                
            result = await db[self.COLLECTION_NAME].find_one({"_id": ObjectId(agent_id)})
            
            if result:
                # Convert ObjectId to string for JSON serialization
                result["_id"] = str(result["_id"])
                if "llm" in result:
                    result["llm"] = str(result["llm"])
                if "capabilities" in result:
                    result["capabilities"] = [str(cap_id) for cap_id in result["capabilities"]]
                if "userId" in result:
                    result["userId"] = str(result["userId"])
                    
                logger.debug(f"Found agent configuration: {result}")
                return result
            else:
                logger.warning(f"No agent found with ID: {agent_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching agent {agent_id}: {str(e)}")
            raise 