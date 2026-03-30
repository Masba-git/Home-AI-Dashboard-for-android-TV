from flask import Blueprint, jsonify, request
import requests
from flask import current_app
from datetime import datetime


weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    """Get current weather using free wttr.in API"""
    city = request.args.get('city', 'London')
    
    try:
        # Using wttr.in - completely free, no API key needed
        url = f'https://wttr.in/{city}?format=j1'
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return jsonify({'error': 'Weather service unavailable'}), 500
        
        data = response.json()
        
        current = data['current_condition'][0]
        
        weather_data = {
            'city': city,
            'temperature': current['temp_C'],
            'feels_like': current['FeelsLikeC'],
            'humidity': current['humidity'],
            'pressure': current['pressure'],
            'description': current['weatherDesc'][0]['value'],
            'icon': f"https:{current['weatherIconUrl'][0]['value']}",
            'wind_speed': current['windspeedKmph'],
            'uv_index': current['uvIndex'],
            'visibility': current['visibility']
        }
        
        return jsonify(weather_data)
    
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@weather_bp.route('/forecast', methods=['GET'])
def get_weather_forecast():
    """Get weather forecast using free wttr.in API"""
    city = request.args.get('city', 'London')
    
    try:
        url = f'https://wttr.in/{city}?format=j1'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        forecast_list = []
        for day in data['weather'][:5]:  # Next 5 days
            forecast_list.append({
                'date': day['date'],
                'day_name': datetime.strptime(day['date'], '%Y-%m-%d').strftime('%A'),
                'temp_min': day['mintempC'],
                'temp_max': day['maxtempC'],
                'description': day['hourly'][0]['weatherDesc'][0]['value'],
                'icon': f"https:{day['hourly'][0]['weatherIconUrl'][0]['value']}"
            })
        
        return jsonify(forecast_list)
    
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500