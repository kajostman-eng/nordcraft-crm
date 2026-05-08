from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "NordKraft AI CRM"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/nordkraft_crm"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Supabase / Auth
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # AI
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # n8n
    N8N_WEBHOOK_BASE: str = "http://localhost:5678/webhook"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://crm.nordkraftgroup.com"]

    # Storage (S3-compatible)
    S3_BUCKET: str = "nordkraft-crm"
    S3_ENDPOINT: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
