from flask import Blueprint, request, jsonify, current_app
from app import db, socketio
from app.models.message import Message
from app.models.user import User
from app.models.sequence import Sequence, SequenceStep
from app.services.ai import ai_service
from datetime import datetime
import json
import logging
import re

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
        
        # Check for action blocks in the response
        processed_response, action_performed = process_ai_action_blocks(ai_response, user.id)
        
        # Save the assistant's response
        assistant_message = Message(
            user_id=user.id,
            content=processed_response,
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

def process_ai_action_blocks(response, user_id):
    """
    Process special action blocks in the AI response to perform workspace actions
    
    Args:
        response (str): The AI response text
        user_id (int): The current user ID
    
    Returns:
        tuple: (processed_response, action_performed)
    """
    # Define regex patterns for action blocks
    create_pattern = r'---ACTION: CREATE_SEQUENCE---(.*?)---END ACTION---'
    add_pattern = r'---ACTION: ADD_STEP---(.*?)---END ACTION---'
    update_pattern = r'---ACTION: UPDATE_STEP---(.*?)---END ACTION---'
    delete_pattern = r'---ACTION: DELETE_STEP---(.*?)---END ACTION---'
    
    # Process CREATE_SEQUENCE actions
    create_match = re.search(create_pattern, response, re.DOTALL)
    if create_match:
        try:
            # Extract and parse JSON
            json_str = create_match.group(1).strip()
            data = json.loads(json_str)
            
            # Create sequence
            sequence = Sequence(
                user_id=user_id,
                title=data.get('title', 'New Sequence'),
                created_at=datetime.utcnow()
            )
            db.session.add(sequence)
            db.session.commit()
            
            # Add steps
            for step_data in data.get('steps', []):
                step = SequenceStep(
                    sequence_id=sequence.id,
                    step_number=step_data.get('step_number', 1),
                    content=step_data.get('content', ''),
                    type=step_data.get('type', 'email')
                )
                db.session.add(step)
            
            db.session.commit()
            
            # Emit sequence update event
            socketio.emit('sequence_update', sequence.to_dict())
            
            # Remove action block from response
            processed_response = re.sub(create_pattern, '', response, flags=re.DOTALL).strip()
            
            return processed_response, True
        except Exception as e:
            logger.error(f"Error processing CREATE_SEQUENCE action: {str(e)}")
    
    # Process ADD_STEP actions
    add_match = re.search(add_pattern, response, re.DOTALL)
    if add_match:
        try:
            # Extract and parse JSON
            json_str = add_match.group(1).strip()
            data = json.loads(json_str)
            
            # Get the current sequence (most recent one)
            sequence = Sequence.query.filter_by(user_id=user_id).order_by(Sequence.created_at.desc()).first()
            
            if not sequence:
                # If no sequence exists, create a new one
                sequence = Sequence(
                    user_id=user_id,
                    title='New Sequence',
                    created_at=datetime.utcnow()
                )
                db.session.add(sequence)
                db.session.commit()
            
            # Add new step
            step = SequenceStep(
                sequence_id=sequence.id,
                step_number=data.get('step_number', 1),
                content=data.get('content', ''),
                type=data.get('type', 'email')
            )
            db.session.add(step)
            db.session.commit()
            
            # Reorder steps
            steps = SequenceStep.query.filter_by(sequence_id=sequence.id).order_by(SequenceStep.step_number).all()
            for i, s in enumerate(steps, 1):
                s.step_number = i
            
            db.session.commit()
            
            # Emit sequence update event
            socketio.emit('sequence_update', sequence.to_dict())
            
            # Remove action block from response
            processed_response = re.sub(add_pattern, '', response, flags=re.DOTALL).strip()
            
            return processed_response, True
        except Exception as e:
            logger.error(f"Error processing ADD_STEP action: {str(e)}")
    
    # Process UPDATE_STEP actions
    update_match = re.search(update_pattern, response, re.DOTALL)
    if update_match:
        try:
            # Extract and parse JSON
            json_str = update_match.group(1).strip()
            data = json.loads(json_str)
            
            # Get the current sequence
            sequence = Sequence.query.filter_by(user_id=user_id).order_by(Sequence.created_at.desc()).first()
            
            if sequence:
                # Find the step by step_number
                step = SequenceStep.query.filter_by(
                    sequence_id=sequence.id,
                    step_number=data.get('step_number')
                ).first()
                
                if step:
                    # Update step
                    if 'content' in data:
                        step.content = data['content']
                    if 'type' in data:
                        step.type = data['type']
                    
                    db.session.commit()
                    
                    # Emit sequence update event
                    socketio.emit('sequence_update', sequence.to_dict())
            
            # Remove action block from response
            processed_response = re.sub(update_pattern, '', response, flags=re.DOTALL).strip()
            
            return processed_response, True
        except Exception as e:
            logger.error(f"Error processing UPDATE_STEP action: {str(e)}")
    
    # Process DELETE_STEP actions
    delete_match = re.search(delete_pattern, response, re.DOTALL)
    if delete_match:
        try:
            # Extract and parse JSON
            json_str = delete_match.group(1).strip()
            data = json.loads(json_str)
            
            # Get the current sequence
            sequence = Sequence.query.filter_by(user_id=user_id).order_by(Sequence.created_at.desc()).first()
            
            if sequence:
                # Find the step by step_number
                step = SequenceStep.query.filter_by(
                    sequence_id=sequence.id,
                    step_number=data.get('step_number')
                ).first()
                
                if step:
                    # Delete step
                    db.session.delete(step)
                    db.session.commit()
                    
                    # Reorder remaining steps
                    steps = SequenceStep.query.filter_by(sequence_id=sequence.id).order_by(SequenceStep.step_number).all()
                    for i, s in enumerate(steps, 1):
                        s.step_number = i
                    
                    db.session.commit()
                    
                    # Emit sequence update event
                    socketio.emit('sequence_update', sequence.to_dict())
            
            # Remove action block from response
            processed_response = re.sub(delete_pattern, '', response, flags=re.DOTALL).strip()
            
            return processed_response, True
        except Exception as e:
            logger.error(f"Error processing DELETE_STEP action: {str(e)}")
    
    # If no action blocks found or processed
    return response, False


@bp.route('', methods=['DELETE'])
def clear_chat():
    """Clear chat history"""
    user = get_default_user()
    Message.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    return jsonify({'message': 'Chat history cleared'})
