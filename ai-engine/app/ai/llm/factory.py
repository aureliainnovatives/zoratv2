from typing import Dict, Type
from .base import BaseLLM
from .providers.openai import OpenAIProvider
from .providers.gemini import GeminiProvider
from ...models.llm import LLMConfig

class LLMFactory:
    """Factory for creating LLM provider instances"""
    
    # Map of provider names to their implementations
    _providers: Dict[str, Type[BaseLLM]] = {
        "OPENAI": OpenAIProvider,
        "GOOGLE": GeminiProvider
    }
    
    @classmethod
    async def create(cls, config: LLMConfig) -> BaseLLM:
        """Create an LLM provider instance based on configuration"""
        provider_class = cls._providers.get(config.provider)
        if not provider_class:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")
            
        provider = provider_class()
        await provider.initialize(config)
        return provider 