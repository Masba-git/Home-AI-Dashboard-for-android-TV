from flask import Blueprint, jsonify, request
from app.models.database import CalendarEvent, db
from datetime import datetime, timedelta

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/events', methods=['GET'])
def get_events():
    """Get calendar events"""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    query = CalendarEvent.query
    
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(CalendarEvent.start_time >= start)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(CalendarEvent.start_time <= end)
    
    events = query.order_by(CalendarEvent.start_time).all()
    
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'start_time': event.start_time.isoformat() if event.start_time else None,
        'end_time': event.end_time.isoformat() if event.end_time else None,
        'all_day': event.all_day
    } for event in events])

@calendar_bp.route('/events', methods=['POST'])
def create_event():
    """Create new calendar event"""
    data = request.json
    
    event = CalendarEvent(
        title=data.get('title'),
        description=data.get('description'),
        start_time=datetime.fromisoformat(data.get('start_time')),
        end_time=datetime.fromisoformat(data.get('end_time')) if data.get('end_time') else None,
        all_day=data.get('all_day', False)
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'id': event.id,
        'message': 'Event created successfully'
    }), 201

@calendar_bp.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update calendar event"""
    event = CalendarEvent.query.get_or_404(event_id)
    data = request.json
    
    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)
    
    if data.get('start_time'):
        event.start_time = datetime.fromisoformat(data['start_time'])
    
    if data.get('end_time'):
        event.end_time = datetime.fromisoformat(data['end_time'])
    
    event.all_day = data.get('all_day', event.all_day)
    
    db.session.commit()
    
    return jsonify({'message': 'Event updated successfully'})

@calendar_bp.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete calendar event"""
    event = CalendarEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'message': 'Event deleted successfully'})