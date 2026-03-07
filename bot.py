import schedule
import time
import asyncio
import json
import os
import hashlib
from datetime import datetime
from news_fetcher import fetch_all_news, group_similar_news
from ai_processor import analyze_story_group
from publisher import publish_to_channel
from config import POST_INTERVAL_MINUTES

POSTED_FILE = "posted_news.json"

def load_posted():
    if os.path.exists(POSTED_FILE):
        try:
            with open(POSTED_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted)[-200:], f)

def make_hash(title):
    return hashlib.md5(title.lower().strip().encode()).hexdigest()

def filter_new_news(all_news, posted):
    return [item for item in all_news if make_hash(item['title']) not in posted]

def get_topic_key(title):
    """Извлекает ключевую тему из заголовка"""
    words = title.lower().split()
    # Ищем ключевые слова
    key_topics = ['иран', 'китай', 'россия', 'сша', 'украина', 'война', 'конфликт']
    for word in words:
        for topic in key_topics:
            if topic in word:
                return topic
    return words[0] if words else 'новости'

async def run_news_cycle():
    print(f"\n{'='*50}")
    print(f"🔄 ЦИКЛ НАЧАЛСЯ: {datetime.now().strftime('%H:%M:%S')}")
    
    posted = load_posted()
    
    # 1. Собираем новости
    all_news = fetch_all_news()
    if not all_news:
        print("❌ Нет новостей")
        return
    
    # 2. Фильтруем новые
    new_news = filter_new_news(all_news, posted)
    print(f"📰 Новых: {len(new_news)}")
    
    if len(new_news) < 5:
        print("⏸️ Мало новых новостей")
        return
    
    # 3. Группируем похожие
    groups = group_similar_news(new_news)
    print(f"📊 Найдено групп: {len(groups)}")
    
    # 4. Отбираем лучшие группы (не повторяющиеся)
    published_count = 0
    posted_topics_today = set()
    
    for group in groups[:3]:  # берем топ-3 группы
        # Проверяем, не публиковали ли уже такую тему сегодня
        topic = get_topic_key(group[0]['title'])
        if topic in posted_topics_today:
            print(f"⏭️ Тема '{topic}' уже была сегодня")
            continue
        
        print(f"✍️ Пишу пост на тему: {topic}")
        post = analyze_story_group(group)
        
        if post:
            # Проверяем качество поста
            if len(post.split('.')) >= 2:  # минимум 2 предложения
                await publish_to_channel(post)
                
                # Помечаем как опубликованные
                for item in group:
                    posted.add(make_hash(item['title']))
                
                posted_topics_today.add(topic)
                published_count += 1
                print(f"✅ Опубликован пост #{published_count}")
                
                # Ждем между постами
                await asyncio.sleep(30)
            else:
                print("❌ Пост слишком короткий")
        else:
            print("❌ Не удалось сгенерировать пост")
    
    save_posted(posted)
    print(f"🎯 Цикл завершен. Опубликовано: {published_count}")

def scheduled_job():
    asyncio.run(run_news_cycle())

def main():
    print("🚀 WORLD AI NEWS ЗАПУЩЕН")
    print(f"⏰ Интервал: {POST_INTERVAL_MINUTES} минут")
    print("📋 Режим: качественные посты, без повторов\n")
    
    scheduled_job()
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(scheduled_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()