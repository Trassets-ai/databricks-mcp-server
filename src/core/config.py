"""
Configuration settings for the Databricks MCP server.
"""

import warnings
from typing import Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    warnings.warn("python-dotenv not found, environment variables must be set manually")

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

VERSION = "0.1.0"


class Settings(BaseSettings):
    """Base settings for the application."""

    DATABRICKS_HOST: str = "https://example.databricks.net"
    DATABRICKS_TOKEN: str = "dapi_token_placeholder"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    VERSION: str = VERSION

    @field_validator("DATABRICKS_HOST")
    def validate_databricks_host(cls, v: str) -> str:
        """Validate Databricks host URL."""
        if not v.startswith(("https://", "http://")):
            raise ValueError("DATABRICKS_HOST must start with http:// or https://")
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


# Create global settings instance
settings = Settings()


def get_api_headers() -> Dict[str, str]:
    """Get headers for Databricks API requests."""
    return {
        "Authorization": f"Bearer {settings.DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }


def get_databricks_api_url(endpoint: str) -> str:
    """
    Construct the full Databricks API URL.
    
    Args:
        endpoint: The API endpoint path, e.g., "/api/2.0/clusters/list"
    
    Returns:
        Full URL to the Databricks API endpoint
    """
    # Ensure endpoint starts with a slash
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    # Remove trailing slash from host if present
    host = settings.DATABRICKS_HOST.rstrip("/")
    
    return f"{host}{endpoint}" 