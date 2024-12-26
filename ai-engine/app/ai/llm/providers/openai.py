from typing import List, Dict, Any, AsyncGenerator
import logging
from openai import OpenAI, AsyncOpenAI
from ..base import BaseLLM
from ....models.llm import LLMConfig

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLM):
    """OpenAI provider implementation"""
    
    def __init__(self):
        self.client = None
        self.config = None
    
    async def initialize(self, config: LLMConfig) -> None:
        """Initialize OpenAI client with configuration"""
        try:
            logger.info(f"Initializing OpenAI client for model {config.model_name}")
            self.config = config
            
            # Initialize the OpenAI client
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
            
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat completion using OpenAI"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            logger.debug(f"Sending chat request to OpenAI with {len(messages)} messages")
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            logger.debug("Successfully received response from OpenAI")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error during chat: {str(e)}")
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def generate(self, prompt: str) -> str:
        """Generate text completion using OpenAI"""
        return await self.chat([{"role": "user", "content": prompt}])
    
    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream chat completion using OpenAI"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        try:
            logger.debug(f"Starting streaming chat with {len(messages)} messages")
            stream = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
            
        except Exception as e:
            logger.error(f"OpenAI API error during stream chat: {str(e)}")
            raise RuntimeError(f"OpenAI API error during streaming: {str(e)}") 