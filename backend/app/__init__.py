from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from app.config import Config
from app.database import db

# Create extensions instances
migrate = Migrate()

def register_models(app):
    """Import all models to ensure they are registered with SQLAlchemy.
    
    Args:
        app: The Flask application instance
    """
    # Import all models here to ensure they are registered with SQLAlchemy
    # This is important for Flask-Migrate to detect model changes
    from app.user import models as user_models  # noqa: F401
    from app.storefront import models as storefront_models  # noqa: F401
    
    # Print debug information about registered models
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        print("\n=== Registered Database Models ===")
        print("Available tables:", inspector.get_table_names())
        print("Models in metadata:", list(db.Model.registry._class_registry.keys()))
        print("================================\n")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    # Register models with the app
    with app.app_context():
        register_models(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.user import models  # noqa
    from app.storefront import models as storefront_models  # noqa
    
    # Initialize CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    
    # Register blueprints
    from app.user.controllers import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/api/users')
    
    return app
