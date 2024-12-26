import os
from functools import lru_cache
from ..config.development import DevelopmentSettings
from ..config.production import ProductionSettings

@lru_cache()
def get_settings():
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()

# Create settings instance
settings = get_settings() 