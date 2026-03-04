import feedparser
import requests
from config import RSS_FEEDS, NEWS_API_KEY
from datetime import datetime, timedelta

def fetch_rss_news():
    """Fetch news from multiple RSS feeds"""
    all_news = []
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            source_name = feed.feed.get('title', feed_url)
            
            for entry in feed.entries[:3]:  # Top 3 from each source
                news_item = {
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', entry.get('description', '')),
                    'link': entry.get('link', ''),
                    'source': source_name,
                    'published': entry.get('published', '')
                }
                all_news.append(news_item)
                
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
            continue
    
    return all_news

def fetch_newsapi_headlines():
    """Fetch top headlines from NewsAPI"""
    if not NEWS_API_KEY:
        return []
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=10&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        articles = []
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title', ''),
                'summary': article.get('description', ''),
                'link': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'NewsAPI'),
                'published': article.get('publishedAt', '')
            })
        return articles
        
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []

def get_all_news():
    """Combine all news sources"""
    rss_news = fetch_rss_news()
    api_news = fetch_newsapi_headlines()
    return rss_news + api_news
