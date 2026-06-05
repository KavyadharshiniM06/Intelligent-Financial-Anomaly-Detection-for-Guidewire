from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Insurance Claim Risk Decision Engine"
    # Set a default local PostgreSQL URL for ease of demo
    DATABASE_URL: str = "postgresql+asyncpg://postgres:admin%40123@localhost:5433/insurance_claims"
    DEBUG: bool = True
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def convert_to_async_driver(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()

