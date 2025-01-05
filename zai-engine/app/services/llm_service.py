import importlib
import logging
from typing import Dict, Type, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.ai.llm.providers.base import BaseLLMProvider
from app.core.database import db

logger = logging.getLogger(__name__)

class LLMService:
    """Service to manage LLM providers dynamically based on MongoDB config."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.db: AsyncIOMotorDatabase = None
        self._provider_cache: Dict[str, Type[BaseLLMProvider]] = {}
    
    async def connect(self):
        """Establish database connection."""
        if self.db is None:
            await db.connect()
            self.db = db.get_database()
    
    async def _load_provider_class(self, provider_name: str) -> Optional[Type[BaseLLMProvider]]:
        """Dynamically load provider class based on provider name."""
        try:
            # Convert provider name to module path (e.g., OPENAI -> openai)
            module_name = f"app.ai.llm.providers.{provider_name.lower()}"
            
            # Handle special cases for class names
            if provider_name == "OPENAI":
                class_name = "OpenAIProvider"
            else:
                class_name = f"{provider_name.title()}Provider"
            
            # Try to import the module
            module = importlib.import_module(module_name)
            provider_class = getattr(module, class_name)
            
            # Verify it's a valid provider class
            if not issubclass(provider_class, BaseLLMProvider):
                raise ValueError(f"Invalid provider class: {class_name}")
            
            return provider_class
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load provider {provider_name}: {str(e)}")
            return None
    
    async def get_provider(self, llm_id: str) -> Optional[BaseLLMProvider]:
        """Get LLM provider instance based on MongoDB config."""
        await self.connect()
        
        try:
            # Get LLM config from MongoDB
            config = await self.db.llms.find_one({"_id": ObjectId(llm_id)})
            if not config:
                raise ValueError(f"LLM config not found: {llm_id}")
            
            if not config.get("isActive", False):
                raise ValueError(f"LLM {llm_id} is not active")
            
            provider_name = config["provider"]
            
            # Get provider class from cache or load it
            if provider_name not in self._provider_cache:
                provider_class = await self._load_provider_class(provider_name)
                if provider_class is None:
                    raise ValueError(f"Provider not implemented: {provider_name}")
                self._provider_cache[provider_name] = provider_class
            
            # Create and return provider instance
            return self._provider_cache[provider_name](config)
            
        except Exception as e:
            logger.error(f"Error getting LLM provider: {str(e)}")
            raise
    
    async def list_active_providers(self) -> list:
        """List all active LLM configurations."""
        await self.connect()
        cursor = self.db.llms.find({"isActive": True})
        return await cursor.to_list(length=None)
    
    async def validate_provider(self, llm_id: str) -> bool:
        """Validate if a provider is properly configured and working."""
        try:
            provider = await self.get_provider(llm_id)
            # Try a simple completion as validation
            result = await provider.generate_text("Test message")
            return bool(result)
        except Exception as e:
            logger.error(f"Provider validation failed for {llm_id}: {str(e)}")
            return False 