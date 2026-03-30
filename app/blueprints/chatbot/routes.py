from flask import Blueprint, jsonify, request
from datetime import datetime
import random
import re

chatbot_bp = Blueprint('chatbot', __name__)

# Store chat history
chat_history = {}

# Simple rule-based responses (completely free, no API needed)
responses = {
    'hello': ['Hello! How can I help you today?', 'Hi there! What can I do for you?', 'Greetings! How may I assist?'],
    'how are you': ['I\'m doing great! Thanks for asking.', 'All systems operational! How can I help?', 'Ready to assist you!'],
    'weather': ['I can show you the weather! Check the weather module above.', 'The weather module has current conditions for your location.'],
    'task': ['You can manage your study tasks in the Tasks module. Add, complete, or delete tasks there!', 'Check the Study Tasks section to manage your to-do list.'],
    'news': ['Latest headlines are in the News module. Stay informed!', 'The news section shows top headlines from around the world.'],
    'prayer': ['Prayer times are displayed in the Prayer Times module.', 'Check the prayer times for your location in the dedicated module.'],
    'thanks': ['You\'re welcome!', 'Happy to help!', 'Anytime!'],
    'help': ['I can help you with weather, news, tasks, prayer times, and more! Just ask or use the modules on screen.', 
             'Try asking about weather, tasks, or prayer times. You can also use the buttons on screen!'],
    'default': ['I\'m here to help! Try asking about weather, tasks, or news.', 
                'Not sure about that. Check the dashboard modules for more information!',
                'You can use the modules above to manage your home dashboard.']
}

def get_simple_response(message):
    """Generate simple rule-based response"""
    message_lower = message.lower()
    
    # Check for greetings
    if re.search(r'\b(hi|hello|hey|greetings)\b', message_lower):
        return random.choice(responses['hello'])
    
    # Check for how are you
    if 'how are you' in message_lower or 'how\'s it going' in message_lower:
        return random.choice(responses['how are you'])
    
    # Check for weather
    if 'weather' in message_lower or 'temperature' in message_lower:
        return random.choice(responses['weather'])
    
    # Check for tasks
    if 'task' in message_lower or 'todo' in message_lower or 'to do' in message_lower:
        return random.choice(responses['task'])
    
    # Check for news
    if 'news' in message_lower or 'headline' in message_lower:
        return random.choice(responses['news'])
    
    # Check for prayer
    if 'prayer' in message_lower or 'salat' in message_lower or 'namaz' in message_lower:
        return random.choice(responses['prayer'])
    
    # Check for thanks
    if 'thank' in message_lower or 'thanks' in message_lower:
        return random.choice(responses['thanks'])
    
    # Check for help
    if 'help' in message_lower:
        return random.choice(responses['help'])
    
    # Default response
    return random.choice(responses['default'])

@chatbot_bp.route('/message', methods=['POST'])
def send_message():
    """Send message to AI chatbot (free version)"""
    data = request.json
    message = data.get('message')
    session_id = data.get('session_id', 'default')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        # Initialize chat history for session
        if session_id not in chat_history:
            chat_history[session_id] = []
        
        # Add user message to history
        chat_history[session_id].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get AI response
        ai_response = get_simple_response(message)
        
        # Add AI response to history
        chat_history[session_id].append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit history size
        if len(chat_history[session_id]) > 50:
            chat_history[session_id] = chat_history[session_id][-50:]
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get chat history for session"""
    history = chat_history.get(session_id, [])
    return jsonify(history)

@chatbot_bp.route('/clear/<session_id>', methods=['DELETE'])
def clear_history(session_id):
    """Clear chat history for session"""
    if session_id in chat_history:
        chat_history[session_id] = []
    return jsonify({'message': 'Chat history cleared'})