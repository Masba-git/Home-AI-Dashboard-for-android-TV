from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../app/static')
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Register blueprints
    from app.blueprints.weather import weather_bp
    from app.blueprints.news import news_bp
    from app.blueprints.cctv import cctv_bp
    from app.blueprints.network import network_bp
    from app.blueprints.tasks import tasks_bp
    from app.blueprints.chatbot import chatbot_bp
    from app.blueprints.youtube import youtube_bp
    from app.blueprints.calendar import calendar_bp
    from app.blueprints.prayer import prayer_bp
    from app.blueprints.notes import notes_bp
    from app.blueprints.reminders import reminders_bp
    
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(news_bp, url_prefix='/api/news')
    app.register_blueprint(cctv_bp, url_prefix='/api/cctv')
    app.register_blueprint(network_bp, url_prefix='/api/network')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
    app.register_blueprint(youtube_bp, url_prefix='/api/youtube')
    app.register_blueprint(calendar_bp, url_prefix='/api/calendar')
    app.register_blueprint(prayer_bp, url_prefix='/api/prayer')
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(reminders_bp, url_prefix='/api/reminders')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        """Serve the main dashboard"""
        return app.send_static_file('../templates/index.html')
    
    return app