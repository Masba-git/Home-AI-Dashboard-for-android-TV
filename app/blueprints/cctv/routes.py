from flask import Blueprint, jsonify, request, Response
import cv2
import numpy as np
from flask import current_app
import threading
import time

cctv_bp = Blueprint('cctv', __name__)

# Store camera streams
camera_streams = {}
stream_lock = threading.Lock()

class CameraStream:
    """Handle camera stream operations"""
    def __init__(self, camera_id, url):
        self.camera_id = camera_id
        self.url = url
        self.cap = None
        self.last_frame = None
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Start camera stream"""
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_frames)
        self.thread.daemon = True
        self.thread.start()
    
    def _capture_frames(self):
        """Capture frames continuously"""
        self.cap = cv2.VideoCapture(self.url)
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                _, jpeg = cv2.imencode('.jpg', frame)
                self.last_frame = jpeg.tobytes()
            time.sleep(0.03)  # ~30 fps
    
    def get_frame(self):
        """Get current frame"""
        return self.last_frame
    
    def stop(self):
        """Stop camera stream"""
        self.is_running = False
        if self.cap:
            self.cap.release()

@cctv_bp.route('/streams', methods=['GET'])
def get_streams():
    """Get list of configured camera streams"""
    streams_config = current_app.config['CCTV_STREAMS']
    
    streams = []
    if streams_config:
        for stream in streams_config.split(','):
            if ':' in stream:
                name, url = stream.split(':', 1)
                streams.append({
                    'id': name,
                    'name': name,
                    'url': url
                })
    
    return jsonify(streams)

@cctv_bp.route('/stream/<camera_id>', methods=['GET'])
def stream_video(camera_id):
    """Stream video from camera"""
    streams_config = current_app.config['CCTV_STREAMS']
    
    # Find camera URL
    camera_url = None
    if streams_config:
        for stream in streams_config.split(','):
            if ':' in stream:
                name, url = stream.split(':', 1)
                if name == camera_id:
                    camera_url = url
                    break
    
    if not camera_url:
        return jsonify({'error': 'Camera not found'}), 404
    
    # Initialize camera stream if not exists
    if camera_id not in camera_streams:
        with stream_lock:
            if camera_id not in camera_streams:
                camera_streams[camera_id] = CameraStream(camera_id, camera_url)
                camera_streams[camera_id].start()
    
    def generate():
        """Generate video frames"""
        while True:
            frame = camera_streams[camera_id].get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.03)
    
    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@cctv_bp.route('/snapshot/<camera_id>', methods=['GET'])
def get_snapshot(camera_id):
    """Get single snapshot from camera"""
    streams_config = current_app.config['CCTV_STREAMS']
    
    # Find camera URL
    camera_url = None
    if streams_config:
        for stream in streams_config.split(','):
            if ':' in stream:
                name, url = stream.split(':', 1)
                if name == camera_id:
                    camera_url = url
                    break
    
    if not camera_url:
        return jsonify({'error': 'Camera not found'}), 404
    
    try:
        cap = cv2.VideoCapture(camera_url)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            _, jpeg = cv2.imencode('.jpg', frame)
            return Response(jpeg.tobytes(), mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Could not capture image'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cctv_bp.route('/add', methods=['POST'])
def add_camera():
    """Add new camera stream (requires config update)"""
    data = request.json
    name = data.get('name')
    url = data.get('url')
    
    # In production, you'd want to save this to a database
    # For now, we'll just return success
    return jsonify({'message': 'Camera added successfully', 'name': name, 'url': url})