from flask import Flask
from .extensions import db, migrate, bcrypt, jwt, ma, cors, limiter
from .routes import register_blueprints

def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)

    # 1. LOAD CONFIGURATION FIRST
    # ---------------------------
    # Try to use config.py from project root if present
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

    # 2. INITIALIZE EXTENSIONS
    # ------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)

    # 3. FORCE LOAD MODELS
    # --------------------
    # (Important: Models must be loaded after db.init_app but before routes)
    from app import models

    # 4. REGISTER BLUEPRINTS (ROUTES)
    # -------------------------------
    try:
        register_blueprints(app)
    except Exception as e:
        print(f"Error registering blueprints: {e}")

    # 5. REGISTER ERROR HANDLERS
    # --------------------------
    try:
        from .errors import register_error_handlers
        register_error_handlers(app)
    except Exception:
        pass

    # 6. HEALTH CHECK ROUTE
    # ---------------------
    @app.route('/')
    def health_check():
        return {
            "status": "success", 
            "message": "The Backend is Running!", 
            "service": "Ecommerce API"
        }, 200

    # 7. FINAL RETURN
    # ---------------
    return app