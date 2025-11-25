from flask import Flask
from .extensions import db, migrate, bcrypt, jwt, ma, cors, limiter
from .routes import register_blueprints
from app import models

def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)

    # register routes / blueprints
    register_blueprints(app)

    # === ADD THIS SECTION ===
    @app.route('/')
    def health_check():
        return {
            "status": "success", 
            "message": "The Backend is Running!", 
            "service": "Ecommerce API"
        }, 200
    # ========================

    return app

    # Load default config
    # try to use config.py from project root if present
    app.config.from_object('config.ProductionConfig') if not app.config.get('TESTING') else None
    try:
        app.config.from_pyfile('../config.py', silent=True)
    except Exception:
        try:
            app.config.from_pyfile('config.py', silent=True)
        except Exception:
            pass

    if config_object:
        app.config.from_object(config_object)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)

    # register routes / blueprints
    try:
        register_blueprints(app)
    except Exception:
        pass

    # register error handlers if available
    try:
        from .errors import register_error_handlers
        register_error_handlers(app)
    except Exception:
        pass

    return app
