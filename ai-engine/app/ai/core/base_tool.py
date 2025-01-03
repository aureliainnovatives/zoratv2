import logging
from typing import Dict, Any, Optional
from langchain.tools import BaseTool as LangChainBaseTool
from .tool_config import ToolConfig, ToolInput, ToolOutput

logger = logging.getLogger(__name__)

class BaseTool:
    """Base class for all capability tools"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize tool with configuration"""
        try:
            # Validate config using Pydantic
            self._config = ToolConfig(**config)
            
            # Create LangChain tool instance using a concrete class
            self._tool = _ConcreteLangChainTool(
                name=self._config.name,
                description=self._config.description,
                tool_instance=self
            )
            
            logger.debug(f"Initialized tool: {self.name}")
            
        except Exception as e:
            logger.error(f"Error initializing tool: {str(e)}")
            raise
    
    @property
    def name(self) -> str:
        """Get tool name"""
        return self._config.name
    
    @property
    def description(self) -> str:
        """Get tool description"""
        return self._config.description
    
    @property
    def args_schema(self) -> Dict[str, Any]:
        """Return the tool's parameter schema"""
        return self._config.parameters
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool's functionality - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute")
    
    @property
    def langchain_tool(self) -> LangChainBaseTool:
        """Get the LangChain tool instance"""
        return self._tool

class _ConcreteLangChainTool(LangChainBaseTool):
    """Concrete implementation of LangChain's BaseTool"""
    
    def __init__(self, name: str, description: str, tool_instance: BaseTool):
        """Initialize with tool instance"""
        super().__init__(
            name=name,
            description=description,
            return_direct=False
        )
        self._tool_instance = tool_instance
    
    def _run(self, *args: Any, **kwargs: Any) -> str:
        """Sync run implementation - raises error as we only use async"""
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, **kwargs: Any) -> str:
        """Async run implementation"""
        try:
            # Validate input
            tool_input = ToolInput(input_data=kwargs)
            
            # Execute tool
            result = await self._tool_instance.execute(tool_input.input_data)
            
            # Validate output
            output = ToolOutput(
                success=True,
                result=result
            )
            
            return str(output.result) if output.result else ""
            
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {str(e)}")
            output = ToolOutput(
                success=False,
                error=str(e)
            )
            raise RuntimeError(output.error) 