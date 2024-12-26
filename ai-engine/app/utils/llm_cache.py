from typing import Dict, Optional
import logging
from ..models.llm import LLMConfig

logger = logging.getLogger(__name__)

class LLMCache:
    """In-memory cache for LLM configurations"""
    
    _cache: Dict[str, LLMConfig] = {}
    
    @classmethod
    def get_llm(cls, name: str) -> Optional[LLMConfig]:
        """Get LLM configuration from cache"""
        logger.debug(f"Looking up LLM in cache: {name}")
        llm = cls._cache.get(name)
        if llm:
            logger.debug(f"Cache hit for LLM: {name}")
        else:
            logger.debug(f"Cache miss for LLM: {name}")
        return llm
    
    @classmethod
    def set_llm(cls, llm: LLMConfig) -> None:
        """Add LLM configuration to cache"""
        logger.debug(f"Adding LLM to cache: {llm.name}")
        cls._cache[llm.name] = llm
    
    @classmethod
    def remove_llm(cls, name: str) -> None:
        """Remove LLM configuration from cache"""
        logger.debug(f"Removing LLM from cache: {name}")
        if name in cls._cache:
            del cls._cache[name]
            logger.debug(f"Removed LLM from cache: {name}")
        else:
            logger.debug(f"LLM not found in cache: {name}")
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all LLM configurations from cache"""
        logger.debug("Clearing LLM cache")
        cls._cache.clear()
    
    @classmethod
    def get_all_llms(cls) -> Dict[str, LLMConfig]:
        """Get all cached LLM configurations"""
        logger.debug(f"Getting all LLMs from cache. Count: {len(cls._cache)}")
        return cls._cache.copy() 