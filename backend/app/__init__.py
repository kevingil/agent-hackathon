from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from app.config import Config
from app.database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)
    
    # Initialize CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    
    # Register blueprints
    from app.user.controllers import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/api/users')
    
    return app
