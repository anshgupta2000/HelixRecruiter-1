from flask import Blueprint, request, jsonify, current_app
from app import db, socketio
from app.models.message import Message
from app.models.user import User
from datetime import datetime
import json

bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Temporary user for development (in production, this would use authentication)
def get_default_user():
    user = User.query.filter_by(email='default@example.com').first()
    if not user:
        user = User(name='Default User', email='default@example.com')
        db.session.add(user)
        db.session.commit()
    return user

@bp.route('', methods=['GET'])
def get_messages():
    """Get chat message history"""
    user = get_default_user()
    messages = Message.query.filter_by(user_id=user.id).order_by(Message.timestamp).all()
    return jsonify([message.to_dict() for message in messages])

@bp.route('', methods=['POST'])
def send_message():
    """Process a new user message and generate assistant response"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Message content is required'}), 400
    
    user = get_default_user()
    
    # Save user message
    user_message = Message(
        user_id=user.id,
        content=data['content'],
        role='user',
        timestamp=datetime.utcnow()
    )
    db.session.add(user_message)
    db.session.commit()
    
    # Emit the user message via WebSocket
    socketio.emit('message', user_message.to_dict())
    
    # Placeholder for AI processing logic
    # In a real implementation, this would call an AI service
    
    # Generate placeholder assistant response
    # This would be replaced with actual AI-generated content
    assistant_message = Message(
        user_id=user.id,
        content=f"I'll help you with that request. Let me work on a recruiting sequence based on: '{data['content']}'",
        role='assistant',
        timestamp=datetime.utcnow()
    )
    db.session.add(assistant_message)
    db.session.commit()
    
    # Emit the assistant message via WebSocket
    socketio.emit('message', assistant_message.to_dict())
    
    return jsonify(user_message.to_dict()), 201

@bp.route('', methods=['DELETE'])
def clear_chat():
    """Clear chat history"""
    user = get_default_user()
    Message.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    return jsonify({'message': 'Chat history cleared'})
