from typing import Tuple, AsyncGenerator
import logging
from fastapi import HTTPException
from ..ai.core.agent_pool import AgentPool

logger = logging.getLogger(__name__)

class AgentService:
    @staticmethod
    async def get_index_message() -> str:
        """Return a welcome message for the index route."""
        return "Welcome to Zorat AI Agent Service - Index"
    
    @staticmethod
    async def get_home_message() -> str:
        """Return a welcome message for the home route."""
        return "Welcome to Zorat AI Agent Service - Home"
    
    @staticmethod
    async def process_chat(agent_id: str, session_id: str, user_message: str) -> Tuple[str, str]:
        """
        Process the user's message using the specified agent.
        Returns a tuple of (response, llm_name).
        """
        try:
            logger.info(f"Processing chat message for agent {agent_id}, session {session_id}")
            
            # Get or create agent instance
            agent = await AgentPool.get_agent(agent_id, session_id)
            
            # Process message
            response = await agent.process_message(user_message)
            
            # For now, hardcode llm_name as we're returning it in the response
            # TODO: Get actual LLM name from agent
            llm_name = "GPT-3.5 Turbo"
            
            return response, llm_name
            
        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process chat: {str(e)}"
            ) 