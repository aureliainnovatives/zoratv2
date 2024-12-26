from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class LLMConfig(BaseModel):
    """Pydantic model for LLM configuration"""
    name: str
    description: str
    type: str
    provider: str
    api_key: Optional[str] = Field(default=None, alias="apiKey")
    base_url: Optional[str] = Field(default=None, alias="baseUrl")
    model_name: Optional[str] = Field(default=None, alias="modelName")
    is_active: bool = Field(default=True, alias="isActive")
    max_tokens: Optional[int] = Field(default=4096, alias="maxTokens")
    temperature: Optional[float] = Field(default=0.7)
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "GPT-3.5 Turbo",
                "description": "OpenAI's GPT-3.5 Turbo model",
                "type": "API_BASED",
                "provider": "OPENAI",
                "apiKey": "sk-...",
                "baseUrl": "https://api.openai.com/v1",
                "modelName": "gpt-3.5-turbo",
                "isActive": True,
                "maxTokens": 4096,
                "temperature": 0.7
            }
        }
        # Disable model_ namespace protection to avoid warning
        protected_namespaces = ()
        
    def dict(self, *args, **kwargs):
        """Override dict method to use alias"""
        kwargs["by_alias"] = True
        return super().dict(*args, **kwargs) 