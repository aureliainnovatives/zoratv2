from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, config: Dict):
        """Initialize provider with config from MongoDB."""
        self.config = config
        self.api_key = config.get("apiKey")
        self.base_url = config.get("baseUrl")
        self.model_name = config.get("modelName")
        self.max_tokens = config.get("maxTokens", 2048)
        self.temperature = config.get("temperature", 0.7)
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Generate text completion for a prompt."""
        pass
    
    @abstractmethod
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate chat completion from a list of messages."""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings for one or more texts."""
        pass
    
    def _validate_config(self) -> None:
        """Validate provider configuration."""
        required_fields = ["apiKey", "modelName"]
        missing_fields = [field for field in required_fields if not self.config.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required config fields: {', '.join(missing_fields)}")
    
    def _format_system_prompt(self, system_prompt: Optional[str]) -> str:
        """Format system prompt with default if none provided."""
        return system_prompt or "You are a helpful AI assistant." 