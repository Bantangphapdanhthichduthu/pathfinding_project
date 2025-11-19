from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Pathfinding Service"
    DEBUG: bool = True
    
    # Database
    # relative path from project root
    DATABASE_URL: str = "sqlite:///./app/db/pathfinding.db"
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # Security (tuỳ chọn cho sau)
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:5500"  # Live Server
    ]
    
    # Map image info (pixel coords)
    MAP_WIDTH: int = 8500
    MAP_HEIGHT: int = 7801
    MAP_ORIGIN: str = "bottom-left"  # "top-left" or "bottom-left"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()