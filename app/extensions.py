"""
Unbound Flask extension objects.

Create the extension instances here (uninitialized) to avoid circular imports.
Initialize them in the application factory (app.create_app) using either:
    db.init_app(app)
    migrate.init_app(app, db)
    ...
or by calling init_extensions(app) below.

This file intentionally *does not* import the Flask app.
"""

from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Core DB + migration
db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()

# Auth
jwt: JWTManager = JWTManager()
bcrypt: Bcrypt = Bcrypt()

# Serialization / validation
ma: Marshmallow = Marshmallow()

# CORS
cors: CORS = CORS()

# Rate limiting (very useful to protect public endpoints)
# The Limiter will be configured in init_extensions using app.config values.
limiter: Limiter = Limiter(key_func=get_remote_address, headers_enabled=True)


def init_extensions(app) -> None:
    """
    Convenience initializer for all extensions.

    You can either call this function from your factory:
        init_extensions(app)

    Or initialize extensions individually (app factory currently calls init_app on each).
    This helper also sets sane defaults for limiter and CORS using app.config:

    Expected config keys (all optional):
      - RATELIMIT_DEFAULT (e.g. "200 per day;50 per hour")
      - CORS_ORIGINS     (list or string, passed to flask_cors.CORS)
      - CORS_SUPPORTS_CREDENTIALS (bool)

    Note: Limiter will respect Flask-Limiter config if present.
    """
    # Database and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Authentication + password hashing
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Marshmallow (schema serialization / validation)
    ma.init_app(app)

    # CORS: default to no origins unless configured.
    cors_origins = app.config.get("CORS_ORIGINS", None)
    cors_kwargs = {}
    if cors_origins is not None:
        cors_kwargs["origins"] = cors_origins
    cors_kwargs["supports_credentials"] = app.config.get("CORS_SUPPORTS_CREDENTIALS", False)
    cors.init_app(app, **cors_kwargs)

    # Rate limiter: use app.config['RATELIMIT_DEFAULT'] if present
    limiter.init_app(app)

    # Optionally log initialization
    app.logger.debug("Extensions initialized: db, migrate, jwt, bcrypt, ma, cors, limiter")
