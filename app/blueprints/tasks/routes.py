from flask import Blueprint, jsonify, request
from app.models.database import Task, db
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'completed': task.completed,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'due_date': task.due_date.isoformat() if task.due_date else None
    } for task in tasks])

@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get single task"""
    task = Task.query.get_or_404(task_id)
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'completed': task.completed,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'due_date': task.due_date.isoformat() if task.due_date else None
    })

@tasks_bp.route('/', methods=['POST'])
def create_task():
    """Create new task"""
    data = request.json
    
    task = Task(
        title=data.get('title'),
        description=data.get('description'),
        completed=False
    )
    
    if data.get('due_date'):
        task.due_date = datetime.fromisoformat(data['due_date'])
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'message': 'Task created successfully'
    }), 201

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task"""
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    
    if data.get('due_date'):
        task.due_date = datetime.fromisoformat(data['due_date'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Task updated successfully'
    })

@tasks_bp.route('/<int:task_id>/toggle', methods=['PATCH'])
def toggle_task(task_id):
    """Toggle task completion status"""
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'completed': task.completed,
        'message': 'Task status toggled'
    })

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({
        'message': 'Task deleted successfully'
    })