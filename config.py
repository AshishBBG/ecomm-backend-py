"""
Application configuration.

Usage:
    from config import get_config
    cfg = get_config("development")  # returns the class, or use create_app to load by name/env

Environment variables:
  - FLASK_ENV or APP_CONFIG: choose configuration name (development/testing/production)
  - DATABASE_URL (preferred) or DATABASE_URI: SQLAlchemy database URL
  - SECRET_KEY, JWT_SECRET_KEY
  - RDS_* style or Railway-provided DATABASE_URL are supported; postgres:// is normalized.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

# Optional: load a .env file in development only (uncomment if you rely on .env locally).
# from dotenv import load_dotenv
# load_dotenv(Path(__file__).parent / ".env")


BASE_DIR = Path(__file__).resolve().parent


def _normalize_database_url(url: Optional[str]) -> Optional[str]:
    """
    Normalize common DB URL variants to what SQLAlchemy expects.
    - Prefer DATABASE_URL (Railway / Heroku convention).
    - Convert deprecated "postgres://" scheme to "postgresql+psycopg2://".
    """
    if not url:
        return None
    url = url.strip()
    # Accept both DATABASE_URL and DATABASE_URI names (backwards compatibility)
    # Normalize postgres scheme used by some providers.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url


class BaseConfig:
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "change-me-in-production"))

    # Database - prefer DATABASE_URL (platforms like Railway/Heroku set this)
    DATABASE_URL: Optional[str] = _normalize_database_url(os.getenv("DATABASE_URL") or os.getenv("DATABASE_URI"))

    # For backwards compatibility, allow explicit SQLALCHEMY_DATABASE_URI override
    SQLALCHEMY_DATABASE_URI: str = (
        DATABASE_URL
        or f"sqlite:///{(BASE_DIR / 'instance' / 'ecommerce_dev.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # SQLAlchemy engine pool tuning - override with env vars if needed
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "10")),
        "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30")),
    }

    # Flask-JWT-Extended settings (tunable via env vars)
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", str(60 * 60 * 24)))  # 1 day default
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_SECONDS", str(60 * 60 * 24 * 30)))  # 30 days

    # CORS / Rate limiting (optional)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")  # in prod, set explicit origins
    CORS_SUPPORTS_CREDENTIALS = os.getenv("CORS_SUPPORTS_CREDENTIALS", "false").lower() in ("1", "true", "yes")
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")

    # Application
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    TESTING = False

    # Logging config (basic defaults; your app factory configures structured logging)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_db_name_from_uri(cls, uri: Optional[str] = None) -> Optional[str]:
        """Return last path element of DB URI (suitable for non-sqlite) or None for sqlite."""
        uri = uri or cls.SQLALCHEMY_DATABASE_URI
        if not uri:
            return None
        uri = uri.strip()
        if uri.startswith("sqlite"):
            return None
        # extract after last '/'
        try:
            return uri.rsplit("/", 1)[-1] or None
        except Exception:
            return None


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    # Use a local file DB by default in dev (instance folder)
    SQLALCHEMY_DATABASE_URI = BaseConfig.DATABASE_URL or f"sqlite:///{(BASE_DIR / 'instance' / 'ecommerce_dev.db')}"
    # Enable SQL echo in dev if requested
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() in ("1", "true", "yes")


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    # Use an in-memory SQLite DB for fast tests by default
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URI", "sqlite:///:memory:")
    # Reduce pool size for test runners
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 1,
        "max_overflow": 0,
    }
    JWT_ACCESS_TOKEN_EXPIRES = 60  # short tokens in tests


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    # In production we must have DATABASE_URL set; otherwise fallback to BaseConfig value
    SQLALCHEMY_DATABASE_URI = BaseConfig.DATABASE_URL or BaseConfig.SQLALCHEMY_DATABASE_URI
    # tighten some engine options for production (allow overrides via env)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30")),
    }


# Helper to resolve config by name
def get_config(name: Optional[str] = None):
    """
    Return the config class for a given name (case-insensitive).
    Default resolution order:
      1. provided `name` argument
      2. FLASK_ENV environment variable
      3. APP_CONFIG environment variable
      4. "production"
    """
    name = (name or os.getenv("FLASK_ENV") or os.getenv("APP_CONFIG") or "production").lower()
    mapping = {
        "development": DevelopmentConfig,
        "dev": DevelopmentConfig,
        "testing": TestingConfig,
        "test": TestingConfig,
        "production": ProductionConfig,
        "prod": ProductionConfig,
    }
    return mapping.get(name, ProductionConfig)
