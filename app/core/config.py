"""
Application configuration and environment variables
"""

import os
from pathlib import Path

class Settings:
    """Application settings and configuration"""
    
    # Server Configuration
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", 8000))
    ENV: str = os.environ.get("THINKERBELL_ENV", "development")
    
    # Model Configuration
    MODEL_DIR: str = os.environ.get(
        "THINKERBELL_MODEL_DIR", 
        "models/thinkerbell-encoder-best"
    )
    FALLBACK_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Application Info
    APP_NAME: str = "Thinkerbell Enhanced API"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "AI-powered legal document generation with auto-detection"
    
    # Performance Settings
    WEB_CONCURRENCY: int = int(os.environ.get("WEB_CONCURRENCY", 1))
    MAX_WORKERS: int = int(os.environ.get("MAX_WORKERS", 1))
    
    # Paths
    STATIC_DIR: Path = Path("static")
    CONFIG_DIR: Path = Path("config")
    STYLE_PROFILES_DIR: Path = Path("style_profiles")
    
    # Development settings
    DEBUG: bool = ENV == "development"
    RELOAD: bool = ENV == "development"

# Global settings instance
settings = Settings()
