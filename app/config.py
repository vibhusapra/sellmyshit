from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    bfl_api_key: str
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
    openai_model: str = "gpt-4.1"  # Using GPT-4.1 model
    
    # BFL API Configuration
    bfl_api_base_url: str = "https://api.bfl.ai/v1"
    
    # Web Scraping
    scrape_timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()