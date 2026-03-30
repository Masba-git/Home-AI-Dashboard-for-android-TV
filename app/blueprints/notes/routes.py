from flask import Blueprint, jsonify, request
from app.models.database import Note, db

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/', methods=['GET'])
def get_notes():
    """Get all notes"""
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    return jsonify([{
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'created_at': note.created_at.isoformat() if note.created_at else None,
        'updated_at': note.updated_at.isoformat() if note.updated_at else None
    } for note in notes])

@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get single note"""
    note = Note.query.get_or_404(note_id)
    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'created_at': note.created_at.isoformat() if note.created_at else None,
        'updated_at': note.updated_at.isoformat() if note.updated_at else None
    })

@notes_bp.route('/', methods=['POST'])
def create_note():
    """Create new note"""
    data = request.json
    
    note = Note(
        title=data.get('title', 'Untitled'),
        content=data.get('content', '')
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify({
        'id': note.id,
        'message': 'Note created successfully'
    }), 201

@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update note"""
    note = Note.query.get_or_404(note_id)
    data = request.json
    
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    
    db.session.commit()
    
    return jsonify({'message': 'Note updated successfully'})

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete note"""
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({'message': 'Note deleted successfully'})