from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./credit_risk.db"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Credit Risk AI Assistant"
    
    # Feature Management API
    FEATURE_API_URL: str = "https://api.featuremanagement.com/v1"
    FEATURE_API_KEY: str = ""  # Set this via environment variable
    FEATURE_API_TIMEOUT: int = 30  # seconds
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]  # Update in production
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Model Settings
    MODEL_PATH: str = "./models"
    MODEL_VERSION: str = "v1"
    
    # Risk Assessment
    RISK_THRESHOLD: float = 0.7
    MAX_RISK_SCORE: float = 100.0
    
    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "riskai_password")
    DB_NAME: str = os.getenv("DB_NAME", "risk_ai")
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Security settings
    ALGORITHM: str = "HS256"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # FastAPI backend
    ]
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Cache settings
    CACHE_TTL: int = 300  # seconds
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create global settings instance
settings = Settings()

# Database URL
DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Feature system API headers
FEATURE_API_HEADERS = {
    "Authorization": f"Bearer {settings.FEATURE_API_KEY}",
    "Content-Type": "application/json"
} if settings.FEATURE_API_KEY else {"Content-Type": "application/json"} 