"""
Production-ready config that supports:
 - DATABASE_URL (preferred)
 - Railway MySQL plugin env vars (MYSQLUSER, MYSQLPASSWORD, MYSQLHOST, MYSQLPORT, MYSQLDATABASE)
 - Fallback local sqlite for development/testing.

Behavior:
 - If DATABASE_URL exists use that (normalizes postgres/mysql schemes to SQLAlchemy).
 - If not, look for MYSQL* env vars and build a mysql+pymysql URL.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent


def _normalize_database_url(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    url = raw.strip()
    # Normalize common provider schemes
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+pymysql://", 1)
    return url


def _build_mysql_url_from_env() -> Optional[str]:
    """
    Build a SQLAlchemy-compatible MySQL URL (mysql+pymysql://user:pass@host:port/db).
    Prefer Railway variables like MYSQLUSER, MYSQL_ROOT_PASSWORD, MYSQLHOST, MYSQLPORT, MYSQLDATABASE.
    """
    user = os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER") or os.getenv("DB_USER")
    # Railway sometimes exposes MYSQL_ROOT_PASSWORD or MYSQLPASSWORD
    password = (
        os.getenv("MYSQL_ROOT_PASSWORD")
        or os.getenv("MYSQLPASSWORD")
        or os.getenv("MYSQL_PASSWORD")
        or os.getenv("DB_PASS")
    )
    host = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST") or os.getenv("RAILWAY_PRIVATE_DOMAIN")
    port = os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or "3306"
    db = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE") or os.getenv("DB_NAME")

    if not (user and password and host and db):
        return None

    # URL-encode password (and user) to be safe with special chars
    user_enc = quote_plus(user)
    pw_enc = quote_plus(password)
    return f"mysql+pymysql://{user_enc}:{pw_enc}@{host}:{port}/{db}"


class BaseConfig:
    # Secrets
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)

    # Prefer canonical DATABASE_URL
    _raw_db = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URI")
    DATABASE_URL: Optional[str] = _normalize_database_url(_raw_db)

    # If no DATABASE_URL, attempt to construct a MySQL URL from Railway vars
    if not DATABASE_URL:
        DATABASE_URL = _build_mysql_url_from_env()

    # Final fallback to sqlite for local dev
    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL or f"sqlite:///{(BASE_DIR / 'instance' / 'ecommerce_dev.db')}"

    # SQLAlchemy options (compatible with SQLAlchemy 2.0)
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "future": True,
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "10")),
        "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30")),
    }

    # JWT
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", str(60 * 60 * 24)))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_SECONDS", str(60 * 60 * 24 * 30)))

    # CORS & rate limit
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    CORS_SUPPORTS_CREDENTIALS = os.getenv("CORS_SUPPORTS_CREDENTIALS", "false").lower() in ("1", "true", "yes")
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")

    # App: endpoints & flags
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    TESTING = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def get_db_name_from_uri(cls, uri: Optional[str] = None) -> Optional[str]:
        uri = uri or cls.SQLALCHEMY_DATABASE_URI
        if not uri:
            return None
        uri = uri.strip()
        if uri.startswith("sqlite"):
            return None
        try:
            return uri.rsplit("/", 1)[-1] or None
        except Exception:
            return None


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    SQLALCHEMY_DATABASE_URI = BaseConfig.DATABASE_URL or f"sqlite:///{(BASE_DIR / 'instance' / 'ecommerce_dev.db')}"
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() in ("1", "true", "yes")


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URI", "sqlite:///:memory:")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "future": True,
        "pool_pre_ping": True,
        "pool_size": 1,
        "max_overflow": 0,
    }
    JWT_ACCESS_TOKEN_EXPIRES = 60


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = BaseConfig.DATABASE_URL or BaseConfig.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_ENGINE_OPTIONS = {
        "future": True,
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30")),
    }


def get_config(name: Optional[str] = None):
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
