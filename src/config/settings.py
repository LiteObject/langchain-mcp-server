"""
Application settings and configuration management.
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application settings
    app_name: str = "LangChain Documentation Server"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # API Configuration
    langchain_docs_base: str = "https://python.langchain.com"
    github_api_base: str = "https://api.github.com/repos/langchain-ai/langchain"
    request_timeout: int = 30

    # Optional GitHub token for higher API limits
    github_token: Optional[str] = None

    # Cache settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 300

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    class Config:  # pylint: disable=too-few-public-methods
        """Configuration for the Settings class."""
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_rate_limit_key(self) -> str:
        """Get the rate limit key for caching."""
        return f"rate_limit_{self.rate_limit_requests}_{self.rate_limit_window}"


# Global settings instance
settings = Settings()
