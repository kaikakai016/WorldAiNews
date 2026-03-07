import schedule
import time
import asyncio
import json
import os
import hashlib
from datetime import datetime, timedelta
from news_fetcher import fetch_all_news, group_similar_news
from ai_processor import analyze_story_group
from publisher import publish_to_channel
from config import POST_INTERVAL_MINUTES

POSTED_FILE = "posted_news.json"
STATS_FILE = "bot_stats.json"

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
        json.dump(list(posted)[-500:], f)

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

def make_hash(title):
    return hashlib.md5(title.lower().strip().encode()).hexdigest()

def filter_new_news(all_news, posted):
    return [item for item in all_news if make_hash(item['title']) not in posted]

def extract_topic(title):
    """Извлекает тему из заголовка"""
    words = title.lower().split()
    topics = ['иран', 'китай', 'россия', 'сша', 'украина', 'война', 
              'конфликт', 'танкер', 'атака', 'выборы', 'санкции']
    
    for word in words:
        for topic in topics:
            if topic in word:
                return topic
    return 'разное'

def already_posted_today(topic, stats):
    """Проверяет, не было ли этой темы сегодня"""
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in stats:
        stats[today] = {'topics': {}, 'count': 0}
    
    # Не больше 2 постов на тему в день
    if topic in stats[today]['topics']:
        return stats[today]['topics'][topic] >= 2
    
    return False

def calculate_priority(group):
    """Вычисляет приоритет группы новостей"""
    score = 0
    
    # Чем больше источников, тем важнее
    score += len(group) * 10
    
    # Срочные новости
    urgent_words = ['срочно', 'breaking', 'экстренно', 'только что']
    for item in group:
        if any(word in item['title'].lower() for word in urgent_words):
            score += 50
            break
    
    # Важные слова
    important_words = ['война', 'атака', 'погиб', 'убит', 'санкции', 'кризис']
    for item in group:
        if any(word in item['title'].lower() for word in important_words):
            score += 20
            break
    
    return score

async def run_news_cycle():
    print(f"\n{'='*50}")
    print(f"🔄 ЦИКЛ: {datetime.now().strftime('%H:%M:%S')}")
    
    posted = load_posted()
    stats = load_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Инициализация статистики на сегодня
    if today not in stats:
        stats[today] = {'topics': {}, 'count': 0, 'posts': []}
    
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
    
    if not groups:
        print("❌ Нет групп")
        return
    
    # 4. Вычисляем приоритеты
    priority_groups = []
    for group in groups[:5]:  # топ-5 групп
        topic = extract_topic(group[0]['title'])
        
        # Проверяем, не было ли сегодня
        if already_posted_today(topic, stats):
            print(f"⏭️ Тема '{topic}' уже была сегодня")
            continue
        
        priority = calculate_priority(group)
        priority_groups.append({
            'group': group,
            'topic': topic,
            'priority': priority
        })
    
    # 5. Сортируем по приоритету
    priority_groups.sort(key=lambda x: x['priority'], reverse=True)
    
    # 6. Публикуем лучшие (не больше 3 за цикл)
    published_count = 0
    for item in priority_groups[:3]:
        print(f"✍️ Пишу: {item['topic']} (приоритет {item['priority']})")
        
        post = analyze_story_group(item['group'])
        
        if post and len(post.split('.')) >= 2:  # проверка качества
            await publish_to_channel(post)
            
            # Помечаем как опубликованные
            for news_item in item['group']:
                posted.add(make_hash(news_item['title']))
            
            # Обновляем статистику
            stats[today]['topics'][item['topic']] = stats[today]['topics'].get(item['topic'], 0) + 1
            stats[today]['count'] += 1
            stats[today]['posts'].append({
                'time': datetime.now().strftime('%H:%M'),
                'topic': item['topic'],
                'length': len(post)
            })
            
            published_count += 1
            print(f"✅ Опубликован #{published_count}")
            
            # Пауза между постами
            await asyncio.sleep(30)
        else:
            print("❌ Пост слишком короткий")
    
    # 7. Сохраняем данные
    save_posted(posted)
    save_stats(stats)
    
    print(f"🎯 Итог: {published_count} постов")
    print(f"📊 Сегодня всего: {stats[today]['count']} постов")

def scheduled_job():
    asyncio.run(run_news_cycle())

def main():
    print("🚀 WORLD AI NEWS — ФИНАЛЬНАЯ ВЕРСИЯ")
    print(f"⏰ Интервал: {POST_INTERVAL_MINUTES} минут")
    print("✅ Контроль повторов")
    print("✅ Приоритеты новостей")
    print("✅ Статистика\n")
    
    scheduled_job()
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(scheduled_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()