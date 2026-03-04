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
        
        # Берем 10 свежих новостей (было 3)
        for entry in feed.entries[:10]:
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
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_single_feed, url) for url in RSS_FEEDS]
        
        for future in futures:
            try:
                result = future.result(timeout=8)
                all_news.extend(result)
            except:
                continue
    
    print(f"📰 Собрано {len(all_news)} новостей из {len(RSS_FEEDS)} источников")
    return all_news

def group_similar_news(news_list, min_sources=2):
    """
    Группирует похожие новости
    """
    groups = []
    used = set()
    
    for i, item1 in enumerate(news_list):
        if i in used:
            continue
            
        group = [item1]
        words1 = set(item1['title'].lower().split())
        
        for j, item2 in enumerate(news_list):
            if j <= i or j in used:
                continue
            
            # Проверяем похожесть по ключевым словам
            words2 = set(item2['title'].lower().split())
            common = words1 & words2
            
            # Если много общих слов - это одна тема
            if len(common) >= 3:
                group.append(item2)
                used.add(j)
        
        if len(group) >= min_sources:
            groups.append(group)
            used.add(i)
    
    # Сортируем группы по размеру (самые обсуждаемые первые)
    groups.sort(key=len, reverse=True)
    
    print(f"🔍 Найдено {len(groups)} групп новостей")
    print(f"🏆 Лучшая тема освещается {len(groups[0]) if groups else 0} источниками")
    
    return groups