from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...models.llm import LLMConfig

class BaseLLM(ABC):
    """Base class for LLM implementations"""
    
    @abstractmethod
    async def initialize(self, config: LLMConfig) -> None:
        """Initialize the LLM with configuration"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate chat response"""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def stream_chat(self, messages: List[Dict[str, str]]) -> Any:
        """Stream chat response"""
        pass 