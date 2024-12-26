from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Schema for chat request"""
    user: str = Field(..., description="The user's message")
    llm_name: str = Field(default="GPT-3.5 Turbo", description="Name of the LLM to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": "What is the weather today?",
                "llm_name": "GPT-3.5 Turbo"
            }
        }

class ChatResponse(BaseModel):
    """Schema for chat response"""
    user: str = Field(..., description="The original user message")
    assistant: str = Field(..., description="The AI assistant's response")
    llm_used: str = Field(..., description="The LLM model used for the response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": "What is the weather today?",
                "assistant": "I'm an AI assistant. Based on your question about weather, I would need access to current weather data and your location to provide accurate information.",
                "llm_used": "GPT-3.5 Turbo"
            }
        } 