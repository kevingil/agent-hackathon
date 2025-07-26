from flask import Flask
from app.config import Config
from app.extensions import db, migrate, socketio
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    # Import and register blueprints
    from app.user.controllers import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/api/users')

    return app
