import feedparser, requests, socket
from concurrent.futures import ThreadPoolExecutor
from config import RSS_FEEDS, NEWS_API_KEY
from difflib import SequenceMatcher

def fetch_single_feed(feed_url):
    try:
        socket.setdefaulttimeout(5)
        feed = feedparser.parse(feed_url)
        source_name = feed.feed.get('title', feed_url)
        results = []
        for entry in feed.entries[:3]:
            results.append({'title': entry.get('title', ''), 'summary': entry.get('summary', entry.get('description', '')), 'link': entry.get('link', ''), 'source': source_name, 'published': entry.get('published', '')})
        return results
    except Exception as e:
        print("Feed error: " + str(e))
        return []

def fetch_rss_news():
    all_news = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_single_feed, url): url for url in RSS_FEEDS}
        for future in futures:
            try:
                result = future.result(timeout=8)
                all_news.extend(result)
            except Exception as e:
                print("Timeout: " + str(e))
    print("RSS fetched: " + str(len(all_news)) + " items")
    return all_news

def fetch_newsapi_headlines():
    if not NEWS_API_KEY:
        return []
    try:
        url = "https://newsapi.org/v2/top-headlines?language=en&pageSize=10&apiKey=" + NEWS_API_KEY
        response = requests.get(url, timeout=5)
        data = response.json()
        articles = []
        for article in data.get('articles', []):
            articles.append({'title': article.get('title', ''), 'summary': article.get('description', ''), 'link': article.get('url', ''), 'source': article.get('source', {}).get('name', 'NewsAPI'), 'published': article.get('publishedAt', '')})
        return articles
    except Exception as e:
        print("NewsAPI error: " + str(e))
        return []

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_keywords(title):
    sw = {'the','a','an','in','on','at','to','for','of','and','or','but','is','are','was','were','be','been','has','have','had','will','would','could','should','may','might','as','by','from','with','about','into','after','before','during','says','said','say'}
    return set(title.lower().split()) - sw

def group_similar_news(all_news, similarity_threshold=0.3, min_sources=2):
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
            if item['source'] == other_item['source']:
                continue
            keywords_j = extract_keywords(other_item['title'])
            overlap = len(keywords_i & keywords_j) / min(len(keywords_i), len(keywords_j)) if keywords_i and keywords_j else 0
            if overlap >= similarity_threshold or similar(item['title'], other_item['title']) >= 0.4:
                group.append(other_item)
                used_indices.add(j)
        if len(group) >= min_sources:
            groups.append(group)
            used_indices.add(i)
    groups.sort(key=lambda g: len(g), reverse=True)
    return groups

def get_all_news():
    return fetch_rss_news() + fetch_newsapi_headlines()