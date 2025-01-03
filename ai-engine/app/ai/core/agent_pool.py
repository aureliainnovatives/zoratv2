import logging
from typing import Dict, Optional
from ..models.agent import Agent

logger = logging.getLogger(__name__)

class AgentPool:
    """Manages pool of agent instances with session tracking"""
    _instances: Dict[str, Dict[str, Agent]] = {}  # agent_id -> {session_id -> Agent}
    
    @classmethod
    async def get_agent(cls, agent_id: str, session_id: str) -> Agent:
        """Get or create an agent instance for the given session"""
        try:
            if agent_id not in cls._instances:
                logger.debug(f"Creating new agent pool for agent_id: {agent_id}")
                cls._instances[agent_id] = {}
                
            if session_id not in cls._instances[agent_id]:
                logger.debug(f"Creating new agent instance for session: {session_id}")
                agent = await Agent.create(agent_id, session_id)
                cls._instances[agent_id][session_id] = agent
                
            return cls._instances[agent_id][session_id]
            
        except Exception as e:
            logger.error(f"Error getting agent instance: {str(e)}")
            raise
    
    @classmethod
    def remove_session(cls, agent_id: str, session_id: str) -> None:
        """Remove a session from the pool"""
        try:
            if agent_id in cls._instances and session_id in cls._instances[agent_id]:
                del cls._instances[agent_id][session_id]
                logger.debug(f"Removed session {session_id} for agent {agent_id}")
                
                # Clean up empty agent pools
                if not cls._instances[agent_id]:
                    del cls._instances[agent_id]
                    logger.debug(f"Removed empty agent pool for {agent_id}")
                    
        except Exception as e:
            logger.error(f"Error removing session: {str(e)}")
            raise 