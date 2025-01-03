from typing import Any, Dict, Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .base import BaseCapability
import json
import re
import logging

logger = logging.getLogger(__name__)

class CapabilityTool(BaseTool):
    """LangChain tool that wraps our capabilities."""
    
    name: str
    description: str
    capability: BaseCapability
    
    def __init__(self, capability: BaseCapability):
        """Initialize the tool with a capability."""
        logger.info(f"***************** Creating Tool for Capability: {capability.name} *****************")
        
        super().__init__(
            name=capability.name,
            description=self._format_description(capability),
            func=self._arun,
            coroutine=self._arun
        )
        self.capability = capability
        logger.info(f"Tool created with parameters: {capability.parameters}")
    
    @staticmethod
    def _format_description(capability: BaseCapability) -> str:
        """Format the tool description with parameter information."""
        desc = f"{capability.description}\n\nParameters:\n"
        for param_name, param_type in capability.parameters.items():
            desc += f"- {param_name} ({param_type})\n"
        return desc
    
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Synchronous execution is not supported."""
        raise NotImplementedError("Use async version")
    
    async def _arun(self, tool_input: str, **kwargs: Any) -> Any:
        """Execute the capability asynchronously."""
        logger.info(f"***************** Executing Tool: {self.name} *****************")
        logger.info(f"Tool input: {tool_input}")
        
        try:
            # Parse input
            params = self._parse_input(tool_input)
            logger.info(f"Parsed parameters: {params}")
            
            # Execute capability
            result = await self.capability.execute(params)
            logger.info(f"Tool execution result: {result}")
            return result
            
        except Exception as e:
            error = f"Error executing tool: {str(e)}"
            logger.error(f"***************** Tool Error: {error} *****************")
            return {"error": error}
    
    def _parse_input(self, tool_input: str) -> Dict[str, Any]:
        """Parse and validate input."""
        # First try to parse as JSON
        try:
            params = json.loads(tool_input)
            if not isinstance(params, dict):
                params = {"input": tool_input}
        except json.JSONDecodeError:
            # If not JSON, try to parse key=value pairs
            params = self._parse_key_value_pairs(tool_input)
            
        # Validate and convert parameters
        return self._validate_and_convert_params(params)
    
    def _parse_key_value_pairs(self, input_str: str) -> Dict[str, Any]:
        """Parse key=value pairs from string."""
        params = {}
        pairs = re.findall(r'(\w+)\s*=\s*([^,\n]+)(?:,|\n|$)', input_str)
        
        if pairs:
            for key, value in pairs:
                params[key] = value.strip()
        else:
            # Use entire input as default parameter
            default_param = next(iter(self.capability.parameters.keys()))
            params[default_param] = input_str.strip()
        
        return params
    
    def _validate_and_convert_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert parameters to correct types."""
        validated = {}
        
        for param_name, param_type in self.capability.parameters.items():
            if param_name not in params:
                raise ValueError(f"Missing required parameter: {param_name}")
            
            value = params[param_name]
            
            # Convert to correct type
            if param_type == "string":
                validated[param_name] = str(value)
            elif param_type == "number":
                try:
                    validated[param_name] = float(value)
                except:
                    raise ValueError(f"Parameter {param_name} must be a number")
            elif param_type == "boolean":
                if isinstance(value, str):
                    validated[param_name] = value.lower() == 'true'
                else:
                    validated[param_name] = bool(value)
            else:
                validated[param_name] = value
        
        return validated 