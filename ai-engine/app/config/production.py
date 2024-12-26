from .base import BaseSettings

class ProductionSettings(BaseSettings):
    """Production-specific settings"""
    
    DEBUG: bool = False
    
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017"  # Change in production
    MONGODB_DB_NAME: str = "zoratv2"
    
    # JWT Settings
    JWT_SECRET_KEY: str = ""  # Must be set via environment variable
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""  # Must be set via environment variable
    
    class Config:
        env_prefix = "PROD_" 