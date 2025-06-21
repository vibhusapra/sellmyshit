from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Keys
    replicate_api_token: str
    openai_api_key: str
    
    # Database
    database_url: str = "sqlite:///./sellmyshit.db"
    
    # Application
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "default_secret_key_change_in_production"
    
    # Upload Configuration
    max_upload_size_mb: int = 10
    allowed_image_extensions: str = "jpg,jpeg,png,webp"
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        return [ext.strip() for ext in self.allowed_image_extensions.split(',')]
    
    # Model Versions
    flux_model: str = "black-forest-labs/flux-1.1-pro"  # Still using Replicate for image enhancement
    openai_model: str = "o1-preview"
    
    # Web Scraping
    scrape_timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()