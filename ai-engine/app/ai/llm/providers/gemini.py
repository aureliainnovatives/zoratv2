import logging
from typing import List, Dict, AsyncGenerator
import google.generativeai as genai
from ..base import BaseLLM
from ....models.llm import LLMConfig

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLM):
    """Google Gemini API provider implementation"""
    
    def __init__(self):
        self.model = None
        self.max_tokens = None
        self.temperature = None
    
    async def initialize(self, config: LLMConfig) -> None:
        """Initialize Gemini client with configuration"""
        try:
            genai.configure(api_key=config.api_key)
            self.model = genai.GenerativeModel(
                model_name=config.model_name,
                generation_config={
                    "max_output_tokens": config.max_tokens,
                    "temperature": config.temperature
                }
            )
            self.max_tokens = config.max_tokens
            self.temperature = config.temperature
            logger.info(f"Initialized Gemini provider with model: {config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {str(e)}")
            raise
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat request to Gemini API"""
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat()
            for message in messages:
                if message["role"] == "user":
                    response = chat.send_message(message["content"])
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat error: {str(e)}")
            raise
    
    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream chat response from Gemini API"""
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat()
            for message in messages[:-1]:  # Process all messages except the last one
                if message["role"] == "user":
                    chat.send_message(message["content"])
            
            # Stream the response for the last message
            last_message = messages[-1]
            if last_message["role"] == "user":
                response = chat.send_message(
                    last_message["content"],
                    stream=True
                )
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text
                    
        except Exception as e:
            logger.error(f"Gemini stream chat error: {str(e)}")
            raise 