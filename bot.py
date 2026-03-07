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

def extract_topic(title):
    """Извлекает тему из заголовка"""
    words = title.lower().split()
    topics = ['иран', 'китай', 'россия', 'сша', 'украина', 'война', 
              'конфликт', 'танкер', 'атака', 'выборы', 'санкции', 'израиль']
    
    for word in words:
        for topic in topics:
            if topic in word:
                return topic
    return 'разное'

def is_breaking_news(group):
    """Проверяет, срочная ли новость"""
    urgent_words = ['срочно', 'breaking', 'экстренно', 'только что', '⚡', 
                    'убит', 'погиб', 'атака', 'взрыв', 'война']
    
    for item in group:
        title_lower = item['title'].lower()
        if any(word in title_lower for word in urgent_words):
            return True
    return False

def calculate_priority(group):
    """Вычисляет приоритет группы (0-100)"""
    score = 0
    
    # Количество источников (самый важный фактор)
    score += len(group) * 10
    
    # Срочные новости
    if is_breaking_news(group):
        score += 50
    
    # Важные ключевые слова
    important_words = ['война', 'атака', 'погиб', 'убит', 'санкции', 'кризис', 'ядерный']
    for item in group:
        if any(word in item['title'].lower() for word in important_words):
            score += 20
            break
    
    # Разные источники (запад+восток) - значит важная тема
    sources = set()
    for item in group:
        source = item['source'].lower()
        if 'bbc' in source or 'cnn' in source or 'reuters' in source:
            sources.add('west')
        if 'rt' in source or 'xinhua' in source or 'tass' in source:
            sources.add('east')
    
    if len(sources) >= 2:
        score += 30
    
    return min(score, 100)

def has_new_details(group, last_posts, topic):
    """Проверяет, есть ли новые факты в группе"""
    # Берем последние посты на эту тему
    recent = [p for p in last_posts if p['topic'] == topic][-2:]
    
    if not recent:
        return True  # новых не было - значит новые детали есть
    
    # Сравниваем заголовки
    old_titles = ' '.join([p['title'] for p in recent])
    new_title = group[0]['title']
    
    # Если заголовок сильно отличается - возможно новые детали
    words1 = set(new_title.lower().split())
    words2 = set(old_titles.lower().split())
    common = words1 & words2
    
    # Если меньше 30% общих слов - это другая новость
    if len(common) / max(len(words1), 1) < 0.3:
        return True
    
    return False

def should_post(group, last_posts, topic):
    """Умное решение: публиковать или нет"""
    
    # 1. Срочные новости - ВСЕГДА
    if is_breaking_news(group):
        print(f"⚡ СРОЧНО! Публикуем {topic}")
        return True
    
    # 2. Очень важные (много источников)
    if len(group) >= 5:
        print(f"🔥 ОЧЕНЬ ВАЖНО: {len(group)} источников")
        return True
    
    # 3. Проверяем последние посты
    recent = [p for p in last_posts if p['topic'] == topic][-3:]
    
    if not recent:
        return True  # не было - публикуем
    
    # 4. Если был недавно, проверяем время
    last_post = recent[-1]
    last_time = datetime.fromisoformat(last_post['time'])
    hours_since = (datetime.now() - last_time).seconds / 3600
    
    # Если прошло больше 4 часов - можно снова
    if hours_since > 4:
        # Но проверяем, есть ли новые детали
        if has_new_details(group, last_posts, topic):
            print(f"🔄 Новые детали по {topic} через {hours_since:.1f}ч")
            return True
    
    # 5. Если много новых источников (раньше было 2, теперь 5)
    if len(group) >= 4 and len(recent) > 0:
        if recent[-1].get('sources', 0) < len(group):
            print(f"📊 Больше источников: было {recent[-1].get('sources',0)}, стало {len(group)}")
            return True
    
    print(f"⏭️ Пропускаем {topic} (было {hours_since:.1f}ч назад)")
    return False

# ========== ОЧЕРЕДЬ ПУБЛИКАЦИЙ ==========

def add_to_queue(group, priority, topic):
    """Добавляет пост в очередь"""
    queue = load_queue()
    
    # Преобразуем группу в формат для сохранения
    saved_group = []
    for item in group:
        saved_group.append({
            'title': item['title'],
            'source': item['source'],
            'summary': item.get('summary', '')[:200]
        })
    
    queue.append({
        'group': saved_group,
        'priority': priority,
        'topic': topic,
        'time_added': str(datetime.now()),
        'status': 'pending'
    })
    
    # Сортируем по приоритету
    queue.sort(key=lambda x: x['priority'], reverse=True)
    
    # Оставляем только топ-10
    save_queue(queue[:10])

def get_next_from_queue():
    """Берет следующий пост из очереди"""
    queue = load_queue()
    
    if not queue:
        return None
    
    # Берем первый (с высоким приоритетом)
    next_post = queue[0]
    
    # Удаляем из очереди
    save_queue(queue[1:])
    
    return next_post

# ========== КЛАСС ДЛЯ ВОССТАНОВЛЕНИЯ ГРУППЫ ==========

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
        """Для совместимости со словарем"""
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
        return
    
    # 2. Фильтруем новые
    new_news = filter_new_news(all_news, posted)
    print(f"📰 Новых: {len(new_news)}")
    
    if len(new_news) < 3:
        print("⏸️ Мало новых новостей")
        # Проверяем очередь
        await process_queue()
        return
    
    # 3. Группируем похожие
    groups = group_similar_news(new_news)
    print(f"📊 Найдено групп: {len(groups)}")
    
    if not groups:
        print("❌ Нет групп")
        await process_queue()
        return
    
    # 4. Анализируем группы и добавляем в очередь
    added_to_queue = 0
    for group in groups[:7]:  # топ-7 групп
        topic = extract_topic(group[0]['title'])
        priority = calculate_priority(group)
        
        # Проверяем, стоит ли публиковать
        if should_post(group, stats['days'][today]['posts'], topic):
            add_to_queue(group, priority, topic)
            added_to_queue += 1
            print(f"📥 В очередь: {topic} (приоритет {priority})")
    
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
    
    print(f"📤 Публикую из очереди: {next_post['topic']} (приоритет {next_post['priority']})")
    
    # Восстанавливаем группу как объекты NewsItem
    group = []
    for item_data in next_post['group']:
        group.append(NewsItem(item_data))
    
    # Генерируем и публикуем пост
    post = analyze_story_group(group)
    if post:
        await publish_to_channel(post)
        
        # Обновляем статистику
        stats = load_stats()
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in stats['days']:
            stats['days'][today] = {'posts': [], 'count': 0}
        
        stats['days'][today]['posts'].append({
            'time': str(datetime.now()),
            'topic': next_post['topic'],
            'priority': next_post['priority']
        })
        stats['days'][today]['count'] += 1
        stats['total_posts'] = stats['days'][today]['count']
        save_stats(stats)
        
        print(f"✅ Опубликован из очереди")
        
        # Помечаем как опубликованные в posted (для истории)
        posted = load_posted()
        for item in group:
            posted.add(make_hash(item.title))
        save_posted(posted)
    else:
        print("❌ Не удалось сгенерировать пост")

def scheduled_job():
    asyncio.run(run_news_cycle())

# ========== ЗАПУСК ==========

def main():
    print("🚀 WORLD AI NEWS — ПРОФЕССИОНАЛЬНАЯ ВЕРСИЯ")
    print(f"⏰ Интервал: {POST_INTERVAL_MINUTES} минут")
    print("✅ Умные решения о публикации")
    print("✅ Очередь приоритетов")
    print("✅ Контроль повторов")
    print("✅ Срочные новости без задержек\n")
    
    # Очищаем устаревшую очередь при старте
    queue = load_queue()
    fresh_queue = []
    for item in queue:
        added = datetime.fromisoformat(item['time_added'])
        if (datetime.now() - added).seconds < 3600 * 24:  # не старше 24 часов
            fresh_queue.append(item)
    save_queue(fresh_queue)
    
    scheduled_job()
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(scheduled_job)
    
    # Дополнительная проверка очереди каждые 10 минут
    schedule.every(10).minutes.do(lambda: asyncio.run(process_queue()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()