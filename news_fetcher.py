import feedparser
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from config import RSS_FEEDS
from difflib import SequenceMatcher
import requests

def get_image_from_entry(entry):
    """Извлекает изображение из RSS записи"""
    if hasattr(entry, 'media_content') and entry.media_content:
        for m in entry.media_content:
            if m.get('type', '').startswith('image') or m.get('url', '').endswith(('.jpg', '.jpeg', '.png', '.webp')):
                return m.get('url')
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        return entry.media_thumbnail[0].get('url')
    return None

def fetch_single_feed(feed_url):
    """Загружает одну RSS ленту с обработкой ошибок"""
    try:
        socket.setdefaulttimeout(8)
        
        # Для проблемных сайтов игнорируем SSL
        if 'press' in feed_url or 'ir' in feed_url or 'xinhua' in feed_url:
            ssl._create_default_https_context = ssl._create_unverified_context
        
        # Добавляем User-Agent чтобы не блокировали
        feed = feedparser.parse(feed_url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        if hasattr(feed, 'bozo') and feed.bozo and feed.bozo_exception:
            # Если ошибка парсинга, но записи есть — всё равно берём
            if not feed.entries:
                print(f"⚠️ Проблема с {feed_url}: {feed.bozo_exception}")
                return []
            
        source_name = feed.feed.get('title', feed_url)
        results = []
        
        for entry in feed.entries[:10]:
            if not entry.get('title'):
                continue
                
            results.append({
                'title': entry.get('title', ''),
                'summary': entry.get('summary', entry.get('description', ''))[:300],
                'link': entry.get('link', ''),
                'source': source_name,
                'published': entry.get('published', ''),
                'image': get_image_from_entry(entry)
            })
        return results
        
    except Exception as e:
        print(f"❌ Ошибка RSS {feed_url}: {str(e)[:50]}")
        return []

def fetch_all_news():
    """Собирает ВСЕ новости из RSS источников"""
    all_news = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_single_feed, url): url for url in RSS_FEEDS}
        for future in futures:
            try:
                result = future.result(timeout=10)
                all_news.extend(result)
            except Exception as e:
                print(f"⏱️ Таймаут: {futures[future]}")
    
    print(f"📰 Всего собрано: {len(all_news)} новостей из {len(RSS_FEEDS)} источников")
    return all_news

def calculate_similarity(title1, title2):
    """Вычисляет похожесть двух заголовков"""
    t1 = title1.lower().strip()
    t2 = title2.lower().strip()
    
    ratio = SequenceMatcher(None, t1, t2).ratio()
    
    words1 = set(t1.split())
    words2 = set(t2.split())
    common_words = words1 & words2
    
    keyword_score = len(common_words) / max(len(words1), len(words2)) if words1 and words2 else 0
    
    return max(ratio, keyword_score)

def extract_topic(title):
    """Извлекает основную тему из заголовка"""
    words = title.lower().split()
    
    key_topics = ['иран', 'китай', 'россия', 'сша', 'украина', 'трамп', 'байден',
                  'израиль', 'палестина', 'европа', 'нато', 'война', 'конфликт',
                  'выборы', 'санкции', 'нефть', 'газ', 'экономика']
    
    for word in words:
        for topic in key_topics:
            if topic in word:
                return topic
    
    stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'is'}
    for word in words:
        if word not in stop_words and len(word) > 3:
            return word[:15]
    
    return 'новости'

def group_similar_news(news_list, min_sources=2):
    """Группирует похожие новости"""
    groups = []
    used = set()
    
    news_list.sort(key=lambda x: len(x['title']), reverse=True)
    
    for i, item1 in enumerate(news_list):
        if i in used:
            continue
            
        group = [item1]
        topic1 = extract_topic(item1['title'])
        
        for j, item2 in enumerate(news_list):
            if j <= i or j in used:
                continue
            
            if item1['source'] == item2['source']:
                continue
            
            similarity = calculate_similarity(item1['title'], item2['title'])
            topic2 = extract_topic(item2['title'])
            
            if similarity > 0.5 or topic1 == topic2:
                group.append(item2)
                used.add(j)
        
        if len(group) >= min_sources:
            groups.append(group)
            used.add(i)
    
    groups.sort(key=len, reverse=True)
    
    print(f"🔍 Найдено групп: {len(groups)}")
    for i, group in enumerate(groups[:5]):
        print(f"   Группа {i+1}: {len(group)} источников, тема: {extract_topic(group[0]['title'])}")
    
    return groups

def get_all_news():
    return fetch_all_news()