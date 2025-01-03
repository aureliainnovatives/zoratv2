from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator
from ...models.llm import LLMConfig

class BaseLLM(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def initialize(self, config: LLMConfig) -> None:
        """Initialize the LLM with configuration"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat request and get a response"""
        pass
    
    @abstractmethod
    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream a chat response"""
        pass 