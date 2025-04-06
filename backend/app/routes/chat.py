from flask import Blueprint, request, jsonify, current_app
from app import db, socketio
from app.models.message import Message
from app.models.user import User
from app.services.ai import ai_service
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

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
    
    try:
        # Get recent chat history for context
        recent_messages = Message.query.filter_by(user_id=user.id) \
            .order_by(Message.timestamp.desc()) \
            .limit(10) \
            .all()
        
        # Reverse to get chronological order
        recent_messages.reverse()
        
        # Format messages for the AI service
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
            if msg.id != user_message.id  # Exclude the current message
        ]
        
        # Call the AI service to get a response
        logger.info(f"Sending message to Anthropic API: {data['content']}")
        ai_response = ai_service.get_chat_response(data['content'], chat_history)
        
        # Save the assistant's response
        assistant_message = Message(
            user_id=user.id,
            content=ai_response,
            role='assistant',
            timestamp=datetime.utcnow()
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        # Emit the assistant message via WebSocket
        socketio.emit('message', assistant_message.to_dict())
        
    except Exception as e:
        logger.error(f"Error processing message with AI service: {str(e)}")
        
        # Create an error response
        error_message = Message(
            user_id=user.id,
            content="I apologize, but I encountered an error processing your request. Please try again.",
            role='assistant',
            timestamp=datetime.utcnow()
        )
        db.session.add(error_message)
        db.session.commit()
        
        # Emit the error message via WebSocket
        socketio.emit('message', error_message.to_dict())
    
    return jsonify(user_message.to_dict()), 201

@bp.route('', methods=['DELETE'])
def clear_chat():
    """Clear chat history"""
    user = get_default_user()
    Message.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    return jsonify({'message': 'Chat history cleared'})
