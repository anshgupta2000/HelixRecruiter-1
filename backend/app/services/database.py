from app import db
from app.models.user import User
from app.models.sequence import Sequence, SequenceStep
from app.models.message import Message

def init_db():
    """Initialize the database with default data"""
    # Create default user if it doesn't exist
    default_user = User.query.filter_by(email='default@example.com').first()
    if not default_user:
        default_user = User(
            name='Default User',
            email='default@example.com'
        )
        db.session.add(default_user)
        db.session.commit()
    
    return default_user

def clear_db():
    """Clear all data from the database (for testing)"""
    SequenceStep.query.delete()
    Sequence.query.delete()
    Message.query.delete()
    User.query.delete()
    db.session.commit()
