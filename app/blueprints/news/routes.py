from flask import Blueprint, jsonify, request
import requests
from datetime import datetime
import feedparser
import random
import re

news_bp = Blueprint('news', __name__)

# Free RSS feeds (no API key needed)
FREE_FEEDS = [
    {'name': 'BBC News', 'url': 'http://feeds.bbci.co.uk/news/rss.xml'},
    {'name': 'CNN', 'url': 'http://rss.cnn.com/rss/edition.rss'},
    {'name': 'Reuters', 'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'},
    {'name': 'Al Jazeera', 'url': 'https://www.aljazeera.com/xml/rss/all.xml'},
    {'name': 'TechCrunch', 'url': 'https://techcrunch.com/feed/'}
]

@news_bp.route('/headlines', methods=['GET'])
def get_news_headlines():
    """Get latest news headlines from free RSS feeds"""
    try:
        # Randomly select a feed to reduce load on any single source
        selected_feeds = random.sample(FREE_FEEDS, min(3, len(FREE_FEEDS)))
        
        all_articles = []
        
        for feed_info in selected_feeds:
            try:
                feed = feedparser.parse(feed_info['url'])
                
                for entry in feed.entries[:5]:  # Get top 5 from each feed
                    # Clean description
                    description = entry.get('summary', entry.get('description', ''))
                    # Remove HTML tags
                    description = re.sub(r'<[^>]+>', '', description)[:200]
                    
                    all_articles.append({
                        'title': entry.get('title', 'No title'),
                        'description': description,
                        'url': entry.get('link', '#'),
                        'source': feed_info['name'],
                        'published_at': entry.get('published', datetime.now().isoformat()),
                        'image_url': ''
                    })
            except Exception as e:
                print(f"Error fetching {feed_info['name']}: {e}")
                continue
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        # Limit to 10 articles
        unique_articles = unique_articles[:10]
        
        if not unique_articles:
            # Fallback sample news
            unique_articles = [
                {
                    'title': 'Welcome to Home Dashboard',
                    'description': 'This is a sample news item. Configure RSS feeds in settings.',
                    'url': '#',
                    'source': 'System',
                    'published_at': datetime.now().isoformat()
                }
            ]
        
        return jsonify({
            'total_results': len(unique_articles),
            'articles': unique_articles
        })
    
    except Exception as e:
        print(f"News error: {e}")
        return jsonify({
            'total_results': 1,
            'articles': [{
                'title': 'News service temporarily unavailable',
                'description': 'Please check your internet connection',
                'url': '#',
                'source': 'System',
                'published_at': datetime.now().isoformat()
            }]
        })

@news_bp.route('/search', methods=['GET'])
def search_news():
    """Search news (limited functionality in free version)"""
    query = request.args.get('q', '')
    
    # Return a simple response for search
    return jsonify({
        'total_results': 1,
        'articles': [{
            'title': f'Search for "{query}"',
            'description': 'Full search requires premium API. Please check headlines above.',
            'url': '#',
            'source': 'System',
            'published_at': datetime.now().isoformat()
        }]
    })