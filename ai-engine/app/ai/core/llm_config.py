from typing import Optional
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    """Configuration model for LLMs"""
    
    type: str = Field(..., description="Type of LLM (e.g., openai, google)")
    provider: str = Field(..., description="Provider name (e.g., OPENAI, GOOGLE)")
    model_name: str = Field(..., description="Model name to use")
    api_key: str = Field(..., description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Optional base URL for API")
    max_tokens: int = Field(1000, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Temperature for response generation")
    
    class Config:
        """Pydantic config"""
        frozen = True  # Make config immutable
        extra = "ignore"  # Ignore extra fields 