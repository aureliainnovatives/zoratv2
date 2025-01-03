from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from .base import Agent
from ..llm.factory import LLMFactory
from ..capabilities.registry import registry as capability_registry
import logging

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory for creating agents from database configurations."""
    
    def __init__(self, db: AsyncIOMotorDatabase, llm_factory: LLMFactory):
        """
        Initialize the agent factory.
        
        Args:
            db: MongoDB database instance
            llm_factory: LLM factory instance
        """
        self.db = db
        self.llm_factory = llm_factory
        
    async def create_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Create an agent instance from database configuration.
        
        Args:
            agent_id: ID of the agent in MongoDB
            
        Returns:
            Agent instance if found, None otherwise
        """
        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(agent_id)
            logger.info(f"***************** Looking up agent with ID: {agent_id} *****************")
            
            # Get agent configuration from database
            agent_config = await self.db.agents.find_one({"_id": obj_id})
            if not agent_config:
                logger.error(f"Agent not found with ID: {agent_id}")
                return None
                
            logger.info(f"Found agent config: {agent_config}")
            
            # Get LLM instance using ID
            llm_id = str(agent_config['llm'])
            logger.info(f"Getting LLM with ID: {llm_id}")
            
            # Get LLM config first
            llm_doc = await self.db.llms.find_one({"_id": ObjectId(llm_id)})
            if not llm_doc:
                logger.error(f"LLM not found with ID: {llm_id}")
                return None
                
            # Get LLM instance using name
            llm = await self.llm_factory.get_llm(llm_doc['name'])
            if not llm:
                logger.error(f"Failed to create LLM instance for {llm_doc['name']}")
                return None
                
            # Get capability configurations
            capability_ids = [str(cap_id) for cap_id in agent_config['capabilities']]
            logger.info(f"Getting capabilities with IDs: {capability_ids}")
            
            capability_configs = []
            async for cap in self.db.capabilities.find({"_id": {"$in": [ObjectId(id) for id in capability_ids]}}):
                logger.info(f"Found capability: {cap}")
                capability_configs.append(cap)
                
            # Load capabilities
            logger.info(f"Loading {len(capability_configs)} capabilities")
            capabilities = []
            for config in capability_configs:
                try:
                    capability = capability_registry.get_capability(config['name'])(config)
                    capabilities.append(capability)
                    logger.info(f"Loaded capability: {config['name']}")
                except Exception as e:
                    logger.error(f"Error loading capability {config['name']}: {str(e)}")
                    logger.exception("Detailed error:")
                    
            if not capabilities:
                logger.error("No capabilities loaded for agent")
                return None
                
            # Create and return agent
            logger.info(f"Creating agent with {len(capabilities)} capabilities")
            return Agent(agent_config, llm, capabilities)
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            logger.exception("Detailed error:")
            return None
        
    async def get_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent configuration from database.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent configuration if found, None otherwise
        """
        return await self.db.agents.find_one({"_id": agent_id}) 