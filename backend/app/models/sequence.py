from app import db
from datetime import datetime

class Sequence(db.Model):
    """Sequence model for outreach campaigns"""
    __tablename__ = 'sequences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    steps = db.relationship('SequenceStep', backref='sequence', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Sequence {self.id}: {self.title}>'
    
    def to_dict(self, include_steps=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_steps:
            data['steps'] = [step.to_dict() for step in self.steps]
        
        return data


class SequenceStep(db.Model):
    """SequenceStep model for individual steps in a sequence"""
    __tablename__ = 'sequence_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    sequence_id = db.Column(db.Integer, db.ForeignKey('sequences.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False, default='email')  # 'email', 'message', 'call', 'other'
    
    def __repr__(self):
        return f'<SequenceStep {self.id}: Step {self.step_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sequence_id': self.sequence_id,
            'step_number': self.step_number,
            'content': self.content,
            'type': self.type
        }
