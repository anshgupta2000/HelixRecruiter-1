import os

class Config:
    """Base configuration"""
    # Database configuration
    # Get the DATABASE_URL environment variable and adjust it for PostgreSQL
    db_url = os.environ.get("DATABASE_URL")
    # Handle specific issues with the format for SQLAlchemy if needed
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///helix.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
    
    # Development settings
    DEBUG = True
    TESTING = False
    
    # Socket.IO settings
    SOCKETIO_ASYNC_MODE = 'threading'
