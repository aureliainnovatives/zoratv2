from typing import List, Dict, Any, AsyncGenerator
import logging
import asyncio
import google.generativeai as genai
from ..base import BaseLLM
from ....models.llm import LLMConfig

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLM):
    """Google Gemini provider implementation"""
    
    def __init__(self):
        self.model = None
        self.config = None
    
    async def initialize(self, config: LLMConfig) -> None:
        """Initialize Gemini client with configuration"""
        try:
            logger.info(f"Initializing Gemini client for model {config.model_name}")
            self.config = config
            
            # Configure the Gemini API
            genai.configure(
                api_key=config.api_key,
                transport="rest"  # Use REST API
            )
            
            # Get the specified model
            self.model = genai.GenerativeModel(config.model_name)
            
            logger.info("Gemini client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise RuntimeError(f"Failed to initialize Gemini client: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat completion using Gemini"""
        if not self.model:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            logger.debug(f"Sending chat request to Gemini with {len(messages)} messages")
            
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    gemini_messages.append({
                        "parts": [{"text": msg["content"]}]
                    })
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    gemini_messages,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.config.max_tokens,
                        temperature=self.config.temperature
                    )
                )
            )
            
            if not response or not response.text:
                raise RuntimeError("No response generated")
                
            logger.debug("Successfully received response from Gemini")
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API error during chat: {str(e)}")
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    async def generate(self, prompt: str) -> str:
        """Generate text completion using Gemini"""
        return await self.chat([{"role": "user", "content": prompt}])
    
    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream chat completion using Gemini"""
        if not self.model:
            raise RuntimeError("Gemini client not initialized")
        
        try:
            logger.debug(f"Starting streaming chat with {len(messages)} messages")
            
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    gemini_messages.append({
                        "parts": [{"text": msg["content"]}]
                    })
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            stream = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    gemini_messages,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.config.max_tokens,
                        temperature=self.config.temperature
                    ),
                    stream=True
                )
            )
            
            # Process the stream in chunks
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
            
        except Exception as e:
            logger.error(f"Gemini API error during stream chat: {str(e)}")
            raise RuntimeError(f"Gemini API error during streaming: {str(e)}") 