import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create a declarative base class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
socketio = SocketIO()

def create_app():
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config.from_object('app.config.Config')
    
    # Set secret key from environment variable
    app.secret_key = os.environ.get("SESSION_SECRET", "helix-dev-secret-key")
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize extensions with app
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    with app.app_context():
        # Import models
        from app.models import user, message, sequence
        
        # Create all tables
        db.create_all()
        
        # Register blueprints
        from app.routes import chat, sequences
        app.register_blueprint(chat.bp)
        app.register_blueprint(sequences.bp)
        
        return app
