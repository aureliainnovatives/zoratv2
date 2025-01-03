import logging
from typing import Dict, Any, Optional, List
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import BaseMessage
from ...core.llm_config import LLMConfig

logger = logging.getLogger(__name__)

class OpenAIProvider:
    """OpenAI LLM provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """Initialize OpenAI provider with configuration"""
        try:
            # Initialize ChatOpenAI with validated config
            kwargs = {
                "model_name": config.model_name,
                "openai_api_key": config.api_key,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }
            
            # Add optional base_url if provided
            if config.base_url:
                kwargs["base_url"] = config.base_url
            
            self._llm = ChatOpenAI(**kwargs)
            logger.info(f"Initialized OpenAI provider with model: {config.model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing OpenAI provider: {str(e)}")
            raise
    
    @property
    def llm(self) -> ChatOpenAI:
        """Get the underlying LangChain LLM instance"""
        return self._llm
    
    async def generate(self, messages: List[BaseMessage]) -> str:
        """Generate response for messages"""
        try:
            response = await self._llm.agenerate([messages])
            return response.generations[0][0].text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to the underlying LLM"""
        return getattr(self._llm, name) 