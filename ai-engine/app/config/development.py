from .base import BaseSettings

class DevelopmentSettings(BaseSettings):
    """Development-specific settings"""
    
    DEBUG: bool = True
    
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "zoratv2"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "dev-secret-key"  # Only for development
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""  # Set via environment variable
    
    class Config:
        env_prefix = "DEV_"