from flask import Blueprint, jsonify, request
from app.models.database import Reminder, db
from datetime import datetime

reminders_bp = Blueprint('reminders', __name__)

@reminders_bp.route('/', methods=['GET'])
def get_reminders():
    """Get all reminders"""
    reminders = Reminder.query.order_by(Reminder.date.desc()).all()
    return jsonify([{
        'id': reminder.id,
        'title': reminder.title,
        'description': reminder.description,
        'date': reminder.date.isoformat() if reminder.date else None,
        'created_by': reminder.created_by,
        'completed': reminder.completed
    } for reminder in reminders])

@reminders_bp.route('/', methods=['POST'])
def create_reminder():
    """Create new reminder"""
    data = request.json
    
    reminder = Reminder(
        title=data.get('title'),
        description=data.get('description'),
        created_by=data.get('created_by', 'Family'),
        completed=False
    )
    
    if data.get('date'):
        reminder.date = datetime.fromisoformat(data['date'])
    
    db.session.add(reminder)
    db.session.commit()
    
    return jsonify({
        'id': reminder.id,
        'message': 'Reminder created successfully'
    }), 201

@reminders_bp.route('/<int:reminder_id>', methods=['PUT'])
def update_reminder(reminder_id):
    """Update reminder"""
    reminder = Reminder.query.get_or_404(reminder_id)
    data = request.json
    
    reminder.title = data.get('title', reminder.title)
    reminder.description = data.get('description', reminder.description)
    reminder.completed = data.get('completed', reminder.completed)
    
    if data.get('date'):
        reminder.date = datetime.fromisoformat(data['date'])
    
    db.session.commit()
    
    return jsonify({'message': 'Reminder updated successfully'})

@reminders_bp.route('/<int:reminder_id>/complete', methods=['PATCH'])
def complete_reminder(reminder_id):
    """Mark reminder as completed"""
    reminder = Reminder.query.get_or_404(reminder_id)
    reminder.completed = True
    db.session.commit()
    
    return jsonify({'message': 'Reminder marked as completed'})

@reminders_bp.route('/<int:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    """Delete reminder"""
    reminder = Reminder.query.get_or_404(reminder_id)
    db.session.delete(reminder)
    db.session.commit()
    
    return jsonify({'message': 'Reminder deleted successfully'})