from typing import Optional, List
import logging
from datetime import datetime
from bson import json_util
import json
from ..core.database import MongoDB
from ..models.llm import LLMConfig

logger = logging.getLogger(__name__)

class LLMRepository:
    """Repository for LLM configurations in MongoDB"""
    
    COLLECTION_NAME = "llms"
    
    @staticmethod
    def _convert_mongo_doc(doc: dict) -> dict:
        """Convert MongoDB document to dict suitable for Pydantic"""
        if doc:
            # Remove MongoDB specific fields but keep the rest
            doc_copy = doc.copy()
            if "_id" in doc_copy:
                del doc_copy["_id"]
            if "__v" in doc_copy:
                del doc_copy["__v"]
            
            # Convert datetime objects to ISO format strings
            if "createdAt" in doc_copy:
                doc_copy["createdAt"] = doc_copy["createdAt"].isoformat()
            if "updatedAt" in doc_copy:
                doc_copy["updatedAt"] = doc_copy["updatedAt"].isoformat()
                
            return doc_copy
        return doc
    
    @staticmethod
    def _format_for_logging(doc: dict) -> str:
        """Format document for logging, handling datetime objects"""
        return json.dumps(doc, default=json_util.default)
    
    @staticmethod
    async def get_llm_by_name(name: str) -> Optional[LLMConfig]:
        """Get LLM configuration by name"""
        try:
            logger.debug(f"Searching for LLM with name: {name}")
            # Use case-insensitive regex query
            query = {"name": {"$regex": f"^{name}$", "$options": "i"}}
            logger.debug(f"Query: {json.dumps(query)}")
            
            result = await MongoDB.db[LLMRepository.COLLECTION_NAME].find_one(query)
            
            if result:
                logger.debug(f"Found LLM document: {LLMRepository._format_for_logging(result)}")
                doc = LLMRepository._convert_mongo_doc(result)
                logger.debug(f"Converted document: {LLMRepository._format_for_logging(doc)}")
                return LLMConfig(**doc)
            else:
                logger.warning(f"No LLM found with name: {name}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching LLM by name {name}: {str(e)}")
            raise

    @staticmethod
    async def get_active_llms() -> List[LLMConfig]:
        """Get all active LLM configurations"""
        try:
            logger.debug("Fetching all active LLMs")
            query = {"isActive": True}
            logger.debug(f"Query: {json.dumps(query)}")
            
            cursor = MongoDB.db[LLMRepository.COLLECTION_NAME].find(query)
            llms = []
            
            async for doc in cursor:
                logger.debug(f"Processing LLM document: {LLMRepository._format_for_logging(doc)}")
                converted_doc = LLMRepository._convert_mongo_doc(doc)
                logger.debug(f"Converted document: {LLMRepository._format_for_logging(converted_doc)}")
                llm_config = LLMConfig(**converted_doc)
                llms.append(llm_config)
                logger.debug(f"Added LLM to list: {llm_config.name}")
            
            logger.info(f"Found {len(llms)} active LLMs")
            return llms
            
        except Exception as e:
            logger.error(f"Error fetching active LLMs: {str(e)}")
            raise

    @staticmethod
    async def update_llm(name: str, config: dict) -> Optional[LLMConfig]:
        """Update LLM configuration"""
        try:
            logger.debug(f"Updating LLM {name} with config: {LLMRepository._format_for_logging(config)}")
            result = await MongoDB.db[LLMRepository.COLLECTION_NAME].find_one_and_update(
                {"name": name},
                {"$set": config},
                return_document=True
            )
            
            if result:
                logger.debug(f"Updated LLM document: {LLMRepository._format_for_logging(result)}")
                doc = LLMRepository._convert_mongo_doc(result)
                return LLMConfig(**doc)
            else:
                logger.warning(f"No LLM found to update with name: {name}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating LLM {name}: {str(e)}")
            raise 