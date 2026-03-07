import feedparser
import requests
import socket
from concurrent.futures import ThreadPoolExecutor
from config import RSS_FEEDS, NEWS_API_KEY
from difflib import SequenceMatcher

def get_image_from_entry(entry):
    """Извлекает изображение из RSS записи"""
    if hasattr(entry, 'media_content') and entry.media_content:
        for m in entry.media_content:
            if m.get('type', '').startswith('image') or m.get('url', '').endswith(('.jpg', '.jpeg', '.png', '.webp')):
                return m.get('url')
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        return entry.media_thumbnail[0].get('url')
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image'):
                return enc.get('href') or enc.get('url')
    if hasattr(entry, 'links'):
        for link in entry.links:
            if link.get('type', '').startswith('image'):
                return link.get('href')
    return None

def fetch_single_feed(feed_url):
    """Загружает одну RSS ленту"""
    try:
        socket.setdefaulttimeout(5)
        feed = feedparser.parse(feed_url)
        
        # Проверка на ошибки парсинга
        if hasattr(feed, 'bozo') and feed.bozo and feed.bozo_exception:
            print(f"⚠️ Проблема с {feed_url}: {feed.bozo_exception}")
            
        source_name = feed.feed.get('title', feed_url)
        results = []
        
        # Берем 10 свежих новостей
        for entry in feed.entries[:10]:
            if not entry.get('title'):
                continue
                
            image = get_image_from_entry(entry)
            results.append({
                'title': entry.get('title', ''),
                'summary': entry.get('summary', entry.get('description', ''))[:300],
                'link': entry.get('link', ''),
                'source': source_name,
                'published': entry.get('published', ''),
                'image': image
            })
        return results
    except Exception as e:
        print(f"❌ Ошибка RSS {feed_url}: {str(e)}")
        return []

def fetch_newsapi_headlines():
    """Загружает новости через NewsAPI"""
    if not NEWS_API_KEY:
        return []
    try:
        url = "https://newsapi.org/v2/top-headlines?language=en&pageSize=10&apiKey=" + NEWS_API_KEY
        response = requests.get(url, timeout=5)
        data = response.json()
        articles = []
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title', ''),
                'summary': article.get('description', '')[:300],
                'link': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'NewsAPI'),
                'published': article.get('publishedAt', ''),
                'image': article.get('urlToImage')
            })
        return articles
    except Exception as e:
        print(f"❌ NewsAPI error: {e}")
        return []

def fetch_all_news():
    """Собирает ВСЕ новости из всех источников"""
    all_news = []
    
    # RSS ленты
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_single_feed, url): url for url in RSS_FEEDS}
        for future in futures:
            try:
                result = future.result(timeout=8)
                all_news.extend(result)
            except Exception as e:
                print(f"⏱️ Таймаут: {futures[future]}")
    
    # NewsAPI
    all_news.extend(fetch_newsapi_headlines())
    
    print(f"📰 Всего собрано: {len(all_news)} новостей")
    return all_news

def calculate_similarity(title1, title2):
    """Вычисляет похожесть двух заголовков"""
    # Убираем лишние символы и приводим к нижнему регистру
    t1 = title1.lower().strip()
    t2 = title2.lower().strip()
    
    # Используем SequenceMatcher
    ratio = SequenceMatcher(None, t1, t2).ratio()
    
    # Проверяем ключевые слова
    words1 = set(t1.split())
    words2 = set(t2.split())
    common_words = words1 & words2
    
    # Вес ключевых слов
    keyword_score = len(common_words) / max(len(words1), len(words2)) if words1 and words2 else 0
    
    # Комбинированная оценка
    final_score = max(ratio, keyword_score)
    
    return final_score

def extract_topic(title):
    """Извлекает основную тему из заголовка"""
    words = title.lower().split()
    
    # Ключевые слова для определения темы
    key_topics = ['иран', 'китай', 'россия', 'сша', 'украина', 'война', 
                  'конфликт', 'танкер', 'атака', 'выборы', 'санкции']
    
    for word in words:
        for topic in key_topics:
            if topic in word:
                return topic
    
    # Если не нашли, берем первое значимое слово
    stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'is', 'are'}
    for word in words:
        if word not in stop_words:
            return word[:15]
    
    return 'новости'

def group_similar_news(news_list, min_sources=2):
    """
    Группирует похожие новости (улучшенная версия)
    """
    groups = []
    used = set()
    
    # Сортируем по длине заголовка (более полные заголовки в начале)
    news_list.sort(key=lambda x: len(x['title']), reverse=True)
    
    for i, item1 in enumerate(news_list):
        if i in used:
            continue
            
        group = [item1]
        topic1 = extract_topic(item1['title'])
        
        for j, item2 in enumerate(news_list):
            if j <= i or j in used:
                continue
            
            # Проверяем, не один ли источник
            if item1['source'] == item2['source']:
                continue
            
            # Вычисляем похожесть
            similarity = calculate_similarity(item1['title'], item2['title'])
            
            # Проверяем тему
            topic2 = extract_topic(item2['title'])
            
            # Условия для группировки
            if similarity > 0.5 or topic1 == topic2:
                group.append(item2)
                used.add(j)
        
        # Добавляем группу, если достаточно источников
        if len(group) >= min_sources:
            # Проверяем, что это действительно одна тема (не случайное совпадение)
            if len(group) >= 2:
                groups.append(group)
                used.add(i)
    
    # Сортируем группы по размеру (самые популярные первые)
    groups.sort(key=len, reverse=True)
    
    print(f"🔍 Найдено групп: {len(groups)}")
    for i, group in enumerate(groups[:3]):
        print(f"   Группа {i+1}: {len(group)} источников, тема: {extract_topic(group[0]['title'])}")
    
    return groups

# Для обратной совместимости
def get_all_news():
    return fetch_all_news()

def group_similar_news_old(news_list, similarity_threshold=0.3, min_sources=2):
    """Старая версия для совместимости"""
    return group_similar_news(news_list, min_sources)