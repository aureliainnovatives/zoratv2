from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ToolConfig(BaseModel):
    """Configuration model for tools/capabilities"""
    
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool")
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description="Tool parameters schema"
    )
    
    class Config:
        """Pydantic config"""
        frozen = True  # Make config immutable
        extra = "ignore"  # Ignore extra fields

class ToolInput(BaseModel):
    """Model for tool input validation"""
    
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input data for tool execution"
    )
    
    class Config:
        """Pydantic config"""
        extra = "allow"  # Allow extra fields in input

class ToolOutput(BaseModel):
    """Model for tool output validation"""
    
    success: bool = Field(..., description="Whether the tool execution was successful")
    result: Optional[Dict[str, Any]] = Field(
        None, description="Tool execution result"
    )
    error: Optional[str] = Field(
        None, description="Error message if execution failed"
    )
    
    class Config:
        """Pydantic config"""
        extra = "ignore"  # Ignore extra fields 