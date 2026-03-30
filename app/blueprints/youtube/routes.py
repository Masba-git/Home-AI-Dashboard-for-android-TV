from flask import Blueprint, jsonify, request
from app.models.database import YouTubeVideo, db
import re

youtube_bp = Blueprint('youtube', __name__)

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([^&]+)',
        r'(?:youtu\.be\/)([^?]+)',
        r'(?:youtube\.com\/embed\/)([^?]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@youtube_bp.route('/videos', methods=['GET'])
def get_videos():
    """Get all study videos"""
    videos = YouTubeVideo.query.order_by(YouTubeVideo.added_at.desc()).all()
    return jsonify([{
        'id': video.id,
        'title': video.title,
        'url': video.url,
        'thumbnail': video.thumbnail,
        'watched': video.watched,
        'added_at': video.added_at.isoformat() if video.added_at else None
    } for video in videos])

@youtube_bp.route('/videos', methods=['POST'])
def add_video():
    """Add new study video"""
    data = request.json
    url = data.get('url')
    title = data.get('title')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    thumbnail = f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'
    
    video = YouTubeVideo(
        title=title or f'YouTube Video {video_id}',
        url=url,
        thumbnail=thumbnail,
        watched=False
    )
    
    db.session.add(video)
    db.session.commit()
    
    return jsonify({
        'id': video.id,
        'message': 'Video added successfully'
    }), 201

@youtube_bp.route('/videos/<int:video_id>', methods=['PUT'])
def update_video(video_id):
    """Update video"""
    video = YouTubeVideo.query.get_or_404(video_id)
    data = request.json
    
    video.title = data.get('title', video.title)
    video.watched = data.get('watched', video.watched)
    
    db.session.commit()
    
    return jsonify({'message': 'Video updated successfully'})

@youtube_bp.route('/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    """Delete video"""
    video = YouTubeVideo.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    
    return jsonify({'message': 'Video deleted successfully'})

@youtube_bp.route('/embed/<video_id>', methods=['GET'])
def embed_video(video_id):
    """Get embed URL for video"""
    embed_url = f'https://www.youtube.com/embed/{video_id}'
    return jsonify({'embed_url': embed_url})