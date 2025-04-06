from flask import Blueprint, request, jsonify
from app import db, socketio
from app.models.sequence import Sequence, SequenceStep
from app.models.user import User
from datetime import datetime

bp = Blueprint('sequences', __name__, url_prefix='/api')

# Temporary user for development (in production, this would use authentication)
def get_default_user():
    user = User.query.filter_by(email='default@example.com').first()
    if not user:
        user = User(name='Default User', email='default@example.com')
        db.session.add(user)
        db.session.commit()
    return user

@bp.route('/sequences', methods=['GET'])
def get_sequences():
    """Get all sequences for the current user"""
    user = get_default_user()
    sequences = Sequence.query.filter_by(user_id=user.id).order_by(Sequence.created_at.desc()).all()
    return jsonify([sequence.to_dict() for sequence in sequences])

@bp.route('/sequences/<int:sequence_id>', methods=['GET'])
def get_sequence(sequence_id):
    """Get a specific sequence by ID"""
    user = get_default_user()
    sequence = Sequence.query.filter_by(id=sequence_id, user_id=user.id).first()
    
    if not sequence:
        return jsonify({'error': 'Sequence not found'}), 404
    
    return jsonify(sequence.to_dict())

@bp.route('/sequences', methods=['POST'])
def create_sequence():
    """Create a new sequence"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Sequence title is required'}), 400
    
    user = get_default_user()
    
    sequence = Sequence(
        user_id=user.id,
        title=data['title'],
        created_at=datetime.utcnow()
    )
    
    db.session.add(sequence)
    db.session.commit()
    
    # Emit sequence creation event
    socketio.emit('sequence_update', sequence.to_dict())
    
    return jsonify(sequence.to_dict()), 201

@bp.route('/sequences/<int:sequence_id>', methods=['PUT'])
def update_sequence(sequence_id):
    """Update an existing sequence"""
    user = get_default_user()
    sequence = Sequence.query.filter_by(id=sequence_id, user_id=user.id).first()
    
    if not sequence:
        return jsonify({'error': 'Sequence not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        sequence.title = data['title']
    
    db.session.commit()
    
    # Emit sequence update event
    socketio.emit('sequence_update', sequence.to_dict())
    
    return jsonify(sequence.to_dict())

@bp.route('/sequences/<int:sequence_id>', methods=['DELETE'])
def delete_sequence(sequence_id):
    """Delete a sequence"""
    user = get_default_user()
    sequence = Sequence.query.filter_by(id=sequence_id, user_id=user.id).first()
    
    if not sequence:
        return jsonify({'error': 'Sequence not found'}), 404
    
    db.session.delete(sequence)
    db.session.commit()
    
    return jsonify({'message': 'Sequence deleted'})

@bp.route('/sequences/<int:sequence_id>/steps', methods=['GET'])
def get_steps(sequence_id):
    """Get all steps for a sequence"""
    user = get_default_user()
    sequence = Sequence.query.filter_by(id=sequence_id, user_id=user.id).first()
    
    if not sequence:
        return jsonify({'error': 'Sequence not found'}), 404
    
    steps = SequenceStep.query.filter_by(sequence_id=sequence_id).order_by(SequenceStep.step_number).all()
    return jsonify([step.to_dict() for step in steps])

@bp.route('/sequences/<int:sequence_id>/steps', methods=['POST'])
def add_step(sequence_id):
    """Add a step to a sequence"""
    user = get_default_user()
    sequence = Sequence.query.filter_by(id=sequence_id, user_id=user.id).first()
    
    if not sequence:
        return jsonify({'error': 'Sequence not found'}), 404
    
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Step content is required'}), 400
    
    # Get the next step number
    max_step = db.session.query(db.func.max(SequenceStep.step_number)).filter_by(sequence_id=sequence_id).scalar() or 0
    next_step_number = max_step + 1
    
    step = SequenceStep(
        sequence_id=sequence_id,
        step_number=data.get('step_number', next_step_number),
        content=data['content'],
        type=data.get('type', 'email')
    )
    
    db.session.add(step)
    db.session.commit()
    
    # Emit sequence update event
    socketio.emit('sequence_update', sequence.to_dict())
    
    return jsonify(step.to_dict()), 201

@bp.route('/sequences/<int:sequence_id>/steps/<int:step_id>', methods=['PUT'])
def update_step(sequence_id, step_id):
    """Update a sequence step"""
    user = get_default_user()
    sequence = Sequence.query.filter_by(id=sequence_id, user_id=user.id).first()
    
    if not sequence:
        return jsonify({'error': 'Sequence not found'}), 404
    
    step = SequenceStep.query.filter_by(id=step_id, sequence_id=sequence_id).first()
    
    if not step:
        return jsonify({'error': 'Step not found'}), 404
    
    data = request.get_json()
    
    if 'content' in data:
        step.content = data['content']
    
    if 'type' in data:
        step.type = data['type']
    
    if 'step_number' in data:
        step.step_number = data['step_number']
    
    db.session.commit()
    
    # Emit sequence update event
    socketio.emit('sequence_update', sequence.to_dict())
    
    return jsonify(step.to_dict())

@bp.route('/steps/<int:step_id>', methods=['DELETE'])
def delete_step(step_id):
    """Delete a sequence step"""
    step = SequenceStep.query.get(step_id)
    
    if not step:
        return jsonify({'error': 'Step not found'}), 404
    
    sequence_id = step.sequence_id
    
    # Get the sequence to verify ownership
    user = get_default_user()
    sequence = Sequence.query.filter_by(id=sequence_id, user_id=user.id).first()
    
    if not sequence:
        return jsonify({'error': 'Sequence not found'}), 404
    
    db.session.delete(step)
    db.session.commit()
    
    # Reorder remaining steps
    steps = SequenceStep.query.filter_by(sequence_id=sequence_id).order_by(SequenceStep.step_number).all()
    for i, s in enumerate(steps, 1):
        s.step_number = i
    
    db.session.commit()
    
    # Emit sequence update event
    socketio.emit('sequence_update', sequence.to_dict())
    
    return jsonify({'message': 'Step deleted'})
