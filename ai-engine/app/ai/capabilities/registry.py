from typing import Dict, Type, List
import importlib
import os
from .base import BaseCapability
import logging

logger = logging.getLogger(__name__)

class CapabilityRegistry:
    """Registry for managing and loading capabilities dynamically."""
    
    def __init__(self):
        """Initialize registry."""
        self._capabilities: Dict[str, Type[BaseCapability]] = {}
        self.initialize()
        
    def register(self, name: str, capability_class: Type[BaseCapability]) -> None:
        """
        Register a capability class.
        
        Args:
            name: Name of the capability
            capability_class: The capability class to register
        """
        if not issubclass(capability_class, BaseCapability):
            raise ValueError(f"Capability {name} must inherit from BaseCapability")
        logger.info(f"***************** Registering Capability: {name} *****************")
        self._capabilities[name] = capability_class
        
    def get_capability(self, name: str) -> Type[BaseCapability]:
        """
        Get a capability class by name.
        
        Args:
            name: Name of the capability
            
        Returns:
            The capability class
            
        Raises:
            ValueError if capability not found
        """
        logger.info(f"***************** Looking up Capability: {name} *****************")
        logger.debug(f"Available capabilities: {list(self._capabilities.keys())}")
        
        # Try exact match first
        if name in self._capabilities:
            return self._capabilities[name]
            
        # Try case-insensitive match
        name_lower = name.lower()
        for cap_name, cap_class in self._capabilities.items():
            if cap_name.lower() == name_lower:
                return cap_class
                
        raise ValueError(f"Capability {name} not found")
        
    def initialize(self) -> None:
        """Initialize the registry by loading all capability implementations."""
        implementations_dir = os.path.join(os.path.dirname(__file__), 'implementations')
        logger.info(f"***************** Initializing Capability Registry from: {implementations_dir} *****************")
        
        for filename in os.listdir(implementations_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                logger.info(f"Loading capability module: {module_name}")
                
                try:
                    module = importlib.import_module(f'.implementations.{module_name}', package=__package__)
                    
                    # Look for capability classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseCapability) and 
                            attr != BaseCapability):
                            
                            # Get the capability name from the class
                            capability_name = getattr(attr, 'name', None)
                            if not capability_name:
                                # Convert module_name to title case as fallback
                                capability_name = module_name.replace('_', ' ').title()
                                
                            logger.info(f"Found capability class: {attr_name} with name: {capability_name}")
                            self.register(capability_name, attr)
                                
                except Exception as e:
                    logger.error(f"Error loading capability {module_name}: {str(e)}")
                    logger.exception("Detailed error:")

# Global registry instance
registry = CapabilityRegistry() 