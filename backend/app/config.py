import os

class Config:
    """Base configuration"""
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///helix.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Development settings
    DEBUG = True
    TESTING = False
    
    # Socket.IO settings
    SOCKETIO_ASYNC_MODE = 'threading'
