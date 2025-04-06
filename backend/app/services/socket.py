from app import socketio
from flask import request
from flask_socketio import emit, join_room, leave_room

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected', request.sid)

@socketio.on('join')
def handle_join(data):
    """Join a room (for collaborative editing)"""
    room = data.get('room')
    if room:
        join_room(room)
        emit('room_update', {'message': 'A new user has joined the room'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    """Leave a room"""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('room_update', {'message': 'A user has left the room'}, room=room)

@socketio.on('editing_sequence')
def handle_editing(data):
    """Broadcast that a user is editing a sequence"""
    sequence_id = data.get('sequence_id')
    if sequence_id:
        room = f'sequence_{sequence_id}'
        emit('user_editing', data, room=room, include_self=False)
