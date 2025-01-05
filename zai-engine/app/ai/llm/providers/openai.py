from typing import Dict, List, Optional, Union
import openai
from openai import AsyncOpenAI

from app.ai.llm.providers.base import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """OpenAI implementation of LLM provider."""
    
    def __init__(self, config: Dict):
        """Initialize OpenAI provider."""
        super().__init__(config)
        self._validate_config()
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url or "https://api.openai.com/v1"
        )
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text completion using OpenAI."""
        try:
            response = await self.client.completions.create(
                model=self.model_name,
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].text.strip()
        except openai.OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate chat completion using OpenAI."""
        try:
            # Add system message if provided
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip()
        except openai.OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings using OpenAI."""
        try:
            # Convert single text to list
            if isinstance(texts, str):
                texts = [texts]
            
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",  # Default embedding model
                input=texts
            )
            return [data.embedding for data in response.data]
        except openai.OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}") 