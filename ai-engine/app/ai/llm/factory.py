import logging
from typing import Dict, Any
from langchain_community.chat_models import ChatOpenAI
from .providers.openai import OpenAIProvider
from ..core.llm_config import LLMConfig

logger = logging.getLogger(__name__)

class LLMFactory:
    """Factory for creating LLM instances"""
    
    @staticmethod
    async def create(config: Dict[str, Any]) -> ChatOpenAI:
        """Create an LLM instance based on configuration"""
        try:
            # First validate the config
            llm_config = LLMConfig(**config)
            
            # Check the type
            if llm_config.type.lower() == "openai":
                provider = OpenAIProvider(llm_config)
                return provider.llm
            else:
                raise ValueError(f"Unsupported LLM type: {llm_config.type}")
                
        except Exception as e:
            logger.error(f"Error creating LLM: {str(e)}")
            raise 