from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Insurance Claim Risk Decision Engine"
    # Set a default local PostgreSQL URL for ease of demo
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin%40123@localhost:5433/insurance_claims"
    DEBUG: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
