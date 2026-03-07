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
QUEUE_FILE = "post_queue.json"

# ========== ЗАГРУЗКА/СОХРАНЕНИЕ ==========

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
    return {'days': {}, 'total_posts': 0}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def load_queue():
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)

def make_hash(title):
    return hashlib.md5(title.lower().strip().encode()).hexdigest()

def filter_new_news(all_news, posted):
    return [item for item in all_news if make_hash(item['title']) not in posted]

# ========== ИЗВЛЕЧЕНИЕ ТЕМЫ ==========

def extract_topic(title):
    """Извлекает тему из заголовка"""
    words = title.lower().split()
    
    topics = ['иран', 'китай', 'россия', 'сша', 'украина', 'трамп', 'байден',
              'израиль', 'палестина', 'европа', 'нато', 'война', 'конфликт',
              'выборы', 'санкции', 'нефть', 'газ', 'экономика', 'венесуэла',
              'сирия', 'турция', 'германия', 'франция', 'великобритания',
              'танкер', 'атака', 'взрыв', 'погиб', 'убит']
    
    for word in words:
        for topic in topics:
            if topic in word:
                return topic
    
    stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'is', 
                  'are', 'was', 'were', 'with', 'from', 'by', 'after', 'before', 'during',
                  'says', 'said', 'say', 'tells', 'told'}
    
    for word in words:
        if word not in stop_words and len(word) > 3:
            return word
    
    return 'новости'

# ========== ПРИОРИТЕТЫ ==========

def is_breaking_news(group):
    """Проверяет, срочная ли новость"""
    urgent_words = ['срочно', 'breaking', 'экстренно', 'только что', '⚡', 
                    'убит', 'погиб', 'атака', 'взрыв', 'война', 'катастрофа',
                    'пожар', 'стрельба', 'теракт', 'крушение']
    
    for item in group:
        title_lower = item['title'].lower()
        if any(word in title_lower for word in urgent_words):
            return True
    return False

def calculate_priority(group):
    """Вычисляет приоритет группы (0-100)"""
    score = 0
    
    # Количество источников (до 50 баллов)
    score += min(len(group) * 10, 50)
    
    # Срочные новости
    if is_breaking_news(group):
        score += 30
    
    # Важные ключевые слова
    important_words = ['война', 'атака', 'погиб', 'убит', 'санкции', 'кризис', 
                       'ядерный', 'ракета', 'бомба', 'вторжение']
    for item in group:
        if any(word in item['title'].lower() for word in important_words):
            score += 15
            break
    
    # Разные источники (запад+восток)
    sources = set()
    for item in group:
        source = item['source'].lower()
        if 'bbc' in source or 'cnn' in source or 'reuters' in source:
            sources.add('west')
        if 'rt' in source or 'xinhua' in source or 'tass' in source or 'cgtn' in source:
            sources.add('east')
        if 'al jazeera' in source or 'france' in source or 'dw' in source:
            sources.add('other')
    
    if len(sources) >= 2:
        score += 20
    if len(sources) >= 3:
        score += 10
    
    return min(score, 100)

# ========== ПРОВЕРКА НА ПОВТОРЫ ==========

def has_new_details(group, last_posts, topic):
    """Проверяет, есть ли новые факты (упрощенная версия)"""
    recent = [p for p in last_posts if p['topic'] == topic][-2:]
    
    if not recent:
        return True
    
    # Просто проверяем время - если прошло больше 4 часов, считаем что могут быть новости
    last_post = recent[-1]
    last_time = datetime.fromisoformat(last_post['time'])
    hours_since = (datetime.now() - last_time).seconds / 3600
    
    return hours_since > 4

def should_post(group, last_posts, topic):
    """Умное решение: публиковать или нет"""
    
    # Срочные новости - всегда
    if is_breaking_news(group):
        print(f"⚡ СРОЧНО! Публикуем {topic}")
        return True
    
    # Очень важные (5+ источников)
    if len(group) >= 5:
        print(f"🔥 ОЧЕНЬ ВАЖНО: {len(group)} источников")
        return True
    
    # Проверяем последние посты
    recent = [p for p in last_posts if p['topic'] == topic][-3:]
    
    # Не было - публикуем
    if not recent:
        return True
    
    # Было - проверяем время
    last_post = recent[-1]
    last_time = datetime.fromisoformat(last_post['time'])
    hours_since = (datetime.now() - last_time).seconds / 3600
    
    # Если прошло больше 4 часов - можно снова
    if hours_since > 4:
        print(f"🔄 Прошло {hours_since:.1f}ч, публикуем {topic}")
        return True
    
    # Если источников стало заметно больше
    if len(group) >= 4 and len(recent) > 0:
        last_sources = recent[-1].get('sources', 0)
        if last_sources < len(group):
            print(f"📊 Больше источников: было {last_sources}, стало {len(group)}")
            return True
    
    print(f"⏭️ Пропускаем {topic} (было {hours_since:.1f}ч назад)")
    return False

# ========== ОЧЕРЕДЬ ПУБЛИКАЦИЙ ==========

def add_to_queue(group, priority, topic):
    """Добавляет пост в очередь"""
    queue = load_queue()
    
    saved_group = []
    for item in group[:3]:  # сохраняем только первые 3 для экономии
        saved_group.append({
            'title': item['title'],
            'source': item['source'],
            'summary': item.get('summary', '')[:150]
        })
    
    queue.append({
        'group': saved_group,
        'priority': priority,
        'topic': topic,
        'sources': len(group),
        'time_added': str(datetime.now()),
        'status': 'pending'
    })
    
    # Сортируем по приоритету
    queue.sort(key=lambda x: x['priority'], reverse=True)
    
    # Оставляем только топ-15
    save_queue(queue[:15])

def get_next_from_queue():
    """Берет следующий пост из очереди"""
    queue = load_queue()
    
    if not queue:
        return None
    
    next_post = queue[0]
    save_queue(queue[1:])
    
    return next_post

# ========== КЛАСС ДЛЯ ВОССТАНОВЛЕНИЯ ==========

class NewsItem:
    """Класс для восстановления новости из очереди"""
    def __init__(self, data):
        self.title = data['title']
        self.source = data['source']
        self.summary = data.get('summary', '')
        self.link = data.get('link', '')
        self.published = data.get('published', '')
        self.image = data.get('image', None)
    
    def get(self, key, default=''):
        return getattr(self, key, default)

# ========== ОСНОВНОЙ ЦИКЛ ==========

async def run_news_cycle():
    print(f"\n{'='*50}")
    print(f"🔄 ЦИКЛ: {datetime.now().strftime('%H:%M:%S')}")
    
    posted = load_posted()
    stats = load_stats()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today not in stats['days']:
        stats['days'][today] = {'posts': [], 'count': 0}
    
    # 1. Собираем новости
    all_news = fetch_all_news()
    if not all_news:
        print("❌ Нет новостей")
        await process_queue()
        return
    
    # 2. Фильтруем новые
    new_news = filter_new_news(all_news, posted)
    print(f"📰 Новых: {len(new_news)}")
    
    if len(new_news) < 3:
        print("⏸️ Мало новых новостей (меньше 3)")
        await process_queue()
        return
    
    # 3. Группируем
    groups = group_similar_news(new_news)
    
    if not groups:
        print("❌ Нет групп (нет тем с 2+ источниками)")
        await process_queue()
        return
    
    # 4. Добавляем в очередь
    added_to_queue = 0
    for i, group in enumerate(groups[:10]):  # топ-10 групп
        topic = extract_topic(group[0]['title'])
        priority = calculate_priority(group)
        
        if should_post(group, stats['days'][today]['posts'], topic):
            add_to_queue(group, priority, topic)
            added_to_queue += 1
            print(f"📥 В очередь [{i+1}]: {topic} (приоритет {priority}, {len(group)} источников)")
    
    print(f"📦 Добавлено в очередь: {added_to_queue}")
    
    # 5. Публикуем из очереди
    await process_queue()
    
    # 6. Сохраняем статистику
    stats['total_posts'] = stats['days'][today]['count']
    save_stats(stats)
    
    print(f"📊 Сегодня всего: {stats['days'][today]['count']} постов")

async def process_queue():
    """Обрабатывает очередь публикаций"""
    queue = load_queue()
    
    if not queue:
        print("📭 Очередь пуста")
        return
    
    print(f"📋 В очереди: {len(queue)} постов")
    
    # Публикуем по одному за цикл
    next_post = get_next_from_queue()
    if not next_post:
        return
    
    print(f"📤 Публикую из очереди: {next_post['topic']} (приоритет {next_post['priority']}, {next_post.get('sources', '?')} источников)")
    
    # Восстанавливаем группу
    group = []
    for item_data in next_post['group']:
        group.append(NewsItem(item_data))
    
    # Генерируем пост
    post = analyze_story_group(group)
    
    if post and len(post) > 50:  # проверка, что пост не пустой
        await publish_to_channel(post)
        
        # Обновляем статистику
        stats = load_stats()
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in stats['days']:
            stats['days'][today] = {'posts': [], 'count': 0}
        
        stats['days'][today]['posts'].append({
            'time': str(datetime.now()),
            'topic': next_post['topic'],
            'priority': next_post['priority'],
            'sources': next_post.get('sources', 0)
        })
        stats['days'][today]['count'] += 1
        stats['total_posts'] = stats['days'][today]['count']
        save_stats(stats)
        
        print(f"✅ Опубликован из очереди")
        
        # Помечаем как опубликованные
        posted = load_posted()
        for item in group:
            posted.add(make_hash(item.title))
        save_posted(posted)
    else:
        print("❌ Не удалось сгенерировать пост (пустой или слишком короткий)")

def scheduled_job():
    asyncio.run(run_news_cycle())

# ========== ЗАПУСК ==========

def main():
    print("🚀 WORLD AI NEWS — ФИНАЛЬНАЯ ВЕРСИЯ")
    print(f"⏰ Интервал: {POST_INTERVAL_MINUTES} минут")
    print("✅ 22 проверенных RSS-источника")
    print("✅ Умные приоритеты")
    print("✅ Очередь публикаций")
    print("✅ Контроль повторов")
    print("✅ Стиль Коврина\n")
    
    # Очищаем устаревшую очередь (старше 24 часов)
    queue = load_queue()
    fresh_queue = []
    now = datetime.now()
    for item in queue:
        try:
            added = datetime.fromisoformat(item['time_added'])
            if (now - added).seconds < 3600 * 24:
                fresh_queue.append(item)
        except:
            pass  # если ошибка в дате - пропускаем
    save_queue(fresh_queue)
    
    print(f"📦 Очередь очищена, осталось: {len(fresh_queue)} постов\n")
    
    # Запускаем первый цикл
    scheduled_job()
    
    # Планируем следующие
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(scheduled_job)
    schedule.every(15).minutes.do(lambda: asyncio.run(process_queue()))  # проверка очереди каждые 15 минут
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()