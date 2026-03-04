import feedparser
import requests
from config import RSS_FEEDS, NEWS_API_KEY
from difflib import SequenceMatcher

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

def similar(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_keywords(title):
    """Extract important keywords from title"""
    stop_words = {
        'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or',
        'but', 'is', 'are', 'was', 'were', 'be', 'been', 'has', 'have', 'had',
        'will', 'would', 'could', 'should', 'may', 'might', 'as', 'by', 'from',
        'with', 'about', 'into', 'after', 'before', 'during', 'says', 'said', 'say'
    }
    words = set(title.lower().split()) - stop_words
    return words

def group_similar_news(all_news, similarity_threshold=0.3, min_sources=2):
    """Group news items that cover the same story from different sources"""
    groups = []
    used_indices = set()
    
    for i, item in enumerate(all_news):
        if i in used_indices:
            continue
        
        group = [item]
        keywords_i = extract_keywords(item['title'])
        
        for j, other_item in enumerate(all_news):
            if j <= i or j in used_indices:
                continue
            
            # Skip if same source
            if item['source'] == other_item['source']:
                continue
            
            keywords_j = extract_keywords(other_item['title'])
            
            # Check keyword overlap
            if len(keywords_i) > 0 and len(keywords_j) > 0:
                overlap = len(keywords_i & keywords_j) / min(len(keywords_i), len(keywords_j))
            else:
                overlap = 0
            
            title_similarity = similar(item['title'], other_item['title'])
            
            if overlap >= similarity_threshold or title_similarity >= 0.4:
                group.append(other_item)
                used_indices.add(j)
        
        if len(group) >= min_sources:
            groups.append(group)
            used_indices.add(i)
    
    # Sort by number of sources (most covered first)
    groups.sort(key=lambda g: len(g), reverse=True)
    return groups

def get_all_news():
    """Combine all news sources"""
    rss_news = fetch_rss_news()
    api_news = fetch_newsapi_headlines()
    return rss_news + api_news
