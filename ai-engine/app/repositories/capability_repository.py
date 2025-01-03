import logging
from typing import Optional, Dict, Any
from bson import ObjectId
from ..core.database import MongoDB

logger = logging.getLogger(__name__)

class CapabilityRepository:
    """Repository for capability configurations in MongoDB"""
    
    COLLECTION_NAME = "capabilities"
    
    async def get_by_id(self, capability_id: str) -> Optional[Dict[str, Any]]:
        """Get capability configuration by ID"""
        try:
            db = MongoDB.get_db()
            if db is None:
                raise RuntimeError("Database connection not initialized")
                
            result = await db[self.COLLECTION_NAME].find_one({"_id": ObjectId(capability_id)})
            
            if result:
                # Convert ObjectId to string for JSON serialization
                result["_id"] = str(result["_id"])
                logger.debug(f"Found capability configuration: {result}")
                return result
            else:
                logger.warning(f"No capability found with ID: {capability_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching capability {capability_id}: {str(e)}")
            raise 