from typing import Dict, List, Optional, Union
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from app.ai.llm.providers.base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    """Google Gemini implementation of LLM provider."""
    
    def __init__(self, config: Dict):
        """Initialize Gemini provider."""
        super().__init__(config)
        self._validate_config()
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_name or "gemini-pro",
            generation_config={
                "max_output_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        )
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text completion using Gemini."""
        try:
            response = await self.model.generate_content_async(prompt)
            return self._process_response(response)
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate chat completion using Gemini."""
        try:
            chat = self.model.start_chat(
                history=[],
                system_prompt=self._format_system_prompt(system_prompt)
            )
            
            # Process messages in order
            for message in messages:
                if message["role"] == "user":
                    await chat.send_message_async(message["content"])
                elif message["role"] == "assistant":
                    # Add assistant messages to history
                    chat.history.append({
                        "role": "model",
                        "parts": [message["content"]]
                    })
            
            # Get the last response
            last_message = messages[-1]["content"]
            response = await chat.send_message_async(last_message)
            return self._process_response(response)
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    async def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings using Gemini."""
        try:
            # Convert single text to list
            if isinstance(texts, str):
                texts = [texts]
            
            model = genai.GenerativeModel("embedding-001")
            embeddings = []
            
            for text in texts:
                result = await model.embed_content_async(
                    model="embedding-001",
                    content=text,
                )
                embeddings.append(result.embedding)
            
            return embeddings
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    def _process_response(self, response: GenerateContentResponse) -> str:
        """Process Gemini response and extract text."""
        if not response.text:
            raise RuntimeError("Empty response from Gemini")
        return response.text.strip() 