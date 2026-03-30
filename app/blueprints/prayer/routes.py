from flask import Blueprint, jsonify, request
import requests
from flask import current_app
from datetime import datetime

prayer_bp = Blueprint('prayer', __name__)

@prayer_bp.route('/times', methods=['GET'])
def get_prayer_times():
    """Get daily prayer times"""
    city = request.args.get('city', 'London')
    country = request.args.get('country', 'UK')
    
    # Using Aladhan API (free, no API key required)
    try:
        # Get current date
        today = datetime.now()
        
        url = 'http://api.aladhan.com/v1/timingsByCity'
        params = {
            'city': city,
            'country': country,
            'method': 2  # Islamic Society of North America
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code != 200 or data.get('code') != 200:
            return jsonify({'error': 'Could not fetch prayer times'}), 500
        
        timings = data['data']['timings']
        
        prayer_times = {
            'fajr': timings.get('Fajr'),
            'sunrise': timings.get('Sunrise'),
            'dhuhr': timings.get('Dhuhr'),
            'asr': timings.get('Asr'),
            'maghrib': timings.get('Maghrib'),
            'isha': timings.get('Isha'),
            'date': data['data']['date']['readable'],
            'hijri_date': data['data']['date']['hijri']['date'],
            'city': city,
            'country': country
        }
        
        return jsonify(prayer_times)
    
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@prayer_bp.route('/next', methods=['GET'])
def get_next_prayer():
    """Get next prayer time"""
    city = request.args.get('city', 'London')
    country = request.args.get('country', 'UK')
    
    try:
        # Get prayer times
        url = 'http://api.aladhan.com/v1/timingsByCity'
        params = {
            'city': city,
            'country': country,
            'method': 2
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            return jsonify({'error': 'Could not fetch prayer times'}), 500
        
        timings = data['data']['timings']
        
        # Convert prayer times to datetime objects
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        prayers = [
            ('Fajr', timings.get('Fajr')),
            ('Dhuhr', timings.get('Dhuhr')),
            ('Asr', timings.get('Asr')),
            ('Maghrib', timings.get('Maghrib')),
            ('Isha', timings.get('Isha'))
        ]
        
        # Find next prayer
        next_prayer = None
        for prayer_name, prayer_time in prayers:
            if prayer_time > current_time:
                next_prayer = {
                    'name': prayer_name,
                    'time': prayer_time,
                    'remaining': None  # Calculate remaining time
                }
                break
        
        # If no prayer today, get tomorrow's Fajr
        if not next_prayer:
            next_prayer = {
                'name': 'Fajr (Tomorrow)',
                'time': prayers[0][1],
                'remaining': 'Tomorrow'
            }
        
        return jsonify(next_prayer)
    
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500