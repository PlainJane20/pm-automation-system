"""
Configuration management using environment variables
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Application
    APP_NAME: str = "PM Automation System"
    DEBUG: bool = False

    # JIRA Configuration
    JIRA_URL: str  # e.g., https://yourcompany.atlassian.net
    JIRA_EMAIL: str  # Your JIRA account email
    JIRA_API_TOKEN: str  # Generate at: https://id.atlassian.com/manage/api-tokens
    JIRA_PROJECT_KEY: str = "PILOT"  # Your project key

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./pm_automation.db"  # Default to SQLite
    # For PostgreSQL: postgresql+asyncpg://user:password@localhost/dbname

    # OpenAI (for AI-powered features)
    OPENAI_API_KEY: str = ""  # Optional - for duplicate detection, auto-classification

    # Slack Integration (optional)
    SLACK_BOT_TOKEN: str = ""
    SLACK_NOTIFICATIONS_CHANNEL: str = "#program-status"

    # Email Configuration (optional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "requests@yourcompany.com"

    # Automation Rules Configuration
    STALE_TICKET_DAYS: int = 60
    SLA_CHECK_INTERVAL_MINUTES: int = 30
    DUPLICATE_SIMILARITY_THRESHOLD: float = 0.8

    # Feature Flags
    ENABLE_AI_CLASSIFICATION: bool = False  # Set to True when OPENAI_API_KEY is provided
    ENABLE_SLACK_NOTIFICATIONS: bool = False
    ENABLE_EMAIL_INTAKE: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
