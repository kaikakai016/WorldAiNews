import feedparser
import socket
from concurrent.futures import ThreadPoolExecutor
from config import RSS_FEEDS

def fetch_single_feed(feed_url):
    """Загружает одну RSS ленту"""
    try:
        socket.setdefaulttimeout(5)
        feed = feedparser.parse(feed_url)
        
        source_name = feed.feed.get('title', feed_url)
        results = []
        
        for entry in feed.entries[:5]:  # берем 5 свежих новостей
            if not entry.get('title'):
                continue
                
            results.append({
                'title': entry.get('title', ''),
                'summary': entry.get('summary', entry.get('description', ''))[:300],
                'source': source_name,
            })
        return results
    except Exception as e:
        return []

def fetch_all_news():
    """Собирает все новости параллельно"""
    all_news = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_single_feed, url) for url in RSS_FEEDS]
        
        for future in futures:
            try:
                result = future.result(timeout=8)
                all_news.extend(result)
            except:
                continue
    
    print(f"📰 Собрано {len(all_news)} новостей")
    return all_news

def group_similar_news(news_list, min_sources=2):
    """
    Группирует похожие новости (простым алгоритмом)
    """
    groups = []
    used = set()
    
    for i, item1 in enumerate(news_list):
        if i in used:
            continue
            
        group = [item1]
        
        for j, item2 in enumerate(news_list):
            if j <= i or j in used:
                continue
                
            # Проверяем похожесть по ключевым словам
            words1 = set(item1['title'].lower().split())
            words2 = set(item2['title'].lower().split())
            
            common = words1 & words2
            if len(common) >= 3:  # минимум 3 общих слова
                group.append(item2)
                used.add(j)
        
        if len(group) >= min_sources:
            groups.append(group)
            used.add(i)
    
    # Сортируем группы по размеру
    groups.sort(key=len, reverse=True)
    print(f"🔍 Найдено {len(groups)} групп новостей")
    return groups