"""
Configuration settings for the Databricks MCP server.
"""

import configparser
import json
import os
import subprocess
import warnings
from typing import Dict

import requests

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
    DATABRICKS_TOKEN: str = ""
    DATABRICKS_PROFILE: str = "oauth"
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


def get_bearer_token() -> str:
    """Get a bearer token: DATABRICKS_TOKEN if set, else a Service-Principal token
    if the profile has client_id/client_secret, else a CLI OAuth token.

    ponytail: shells out to the CLI instead of using the SDK, because the SDK
    calls `databricks auth token --host ...`, which the CLI's secure keyring
    cache does not resolve — only `--profile` does. No caching: the CLI caches
    the token itself and only refreshes when it is close to expiry.
    """
    if settings.DATABRICKS_TOKEN:
        return settings.DATABRICKS_TOKEN

    # Service Principal (Profil mit client_id/client_secret): `databricks auth token` kann kein M2M.
    # ponytail: kein Token-Cache, jeder API-Aufruf holt ein neues 1-h-Token; Cache, falls das bremst
    cfg = configparser.RawConfigParser()
    cfg.read(os.path.expanduser("~/.databrickscfg"))
    if cfg.has_option(settings.DATABRICKS_PROFILE, "client_secret"):
        p = cfg[settings.DATABRICKS_PROFILE]
        resp = requests.post(
            p["host"].rstrip("/") + "/oidc/v1/token",
            data={"grant_type": "client_credentials", "scope": "all-apis"},
            auth=(p["client_id"], p["client_secret"]),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    result = subprocess.run(
        ["databricks", "auth", "token", "--profile", settings.DATABRICKS_PROFILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"databricks auth token --profile {settings.DATABRICKS_PROFILE} failed: "
            f"{result.stderr.strip()} — run `databricks auth login --profile "
            f"{settings.DATABRICKS_PROFILE}`"
        )
    return json.loads(result.stdout)["access_token"]


def get_api_headers() -> Dict[str, str]:
    """Get headers for Databricks API requests."""
    return {
        "Authorization": f"Bearer {get_bearer_token()}",
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