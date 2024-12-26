from typing import List
from pydantic_settings import BaseSettings

class BaseSettings(BaseSettings):
    """Base settings for the application"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Zorat AI Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "zoratv2"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    
    class Config:
        case_sensitive = True 