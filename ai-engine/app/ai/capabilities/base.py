from typing import Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseCapability(ABC):
    """Base class for all capabilities."""
    
    name: str = None
    description: str = None
    parameters: Dict[str, str] = {}
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize capability with configuration.
        
        Args:
            config: Configuration dictionary from MongoDB containing:
                - name: Name of the capability
                - description: Description of what the capability does
                - parameters: Dictionary of parameter names and their types
                - Other config specific to the capability
        """
        logger.info(f"***************** Initializing Capability: {self.name} *****************")
        self.config = config
        
        # Override class attributes if provided in config
        if 'name' in config:
            self.name = config['name']
        if 'description' in config:
            self.description = config['description']
        if 'parameters' in config:
            self.parameters = config['parameters']
            
        logger.info(f"Capability parameters: {self.parameters}")
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the capability.
        
        Args:
            input_data: Input data for capability execution, must match parameters defined in config
            
        Returns:
            Result of capability execution
        """
        pass
        
    def validate_parameters(self, input_data: Dict[str, Any]) -> None:
        """
        Validate that input data matches required parameters.
        
        Args:
            input_data: Input data to validate
            
        Raises:
            ValueError: If required parameters are missing or of wrong type
        """
        logger.info(f"Validating parameters for {self.name}: {input_data}")
        
        for param_name, param_type in self.parameters.items():
            if param_name not in input_data:
                error = f"Missing required parameter: {param_name}"
                logger.error(f"***************** Parameter Validation Error: {error} *****************")
                raise ValueError(error)
            
            value = input_data[param_name]
            if param_type == "string" and not isinstance(value, str):
                error = f"Parameter {param_name} must be a string"
                logger.error(f"***************** Parameter Validation Error: {error} *****************")
                raise ValueError(error)
            elif param_type == "number" and not isinstance(value, (int, float)):
                error = f"Parameter {param_name} must be a number"
                logger.error(f"***************** Parameter Validation Error: {error} *****************")
                raise ValueError(error)
            elif param_type == "boolean" and not isinstance(value, bool):
                error = f"Parameter {param_name} must be a boolean"
                logger.error(f"***************** Parameter Validation Error: {error} *****************")
                raise ValueError(error)
                
        logger.info("Parameter validation successful") 