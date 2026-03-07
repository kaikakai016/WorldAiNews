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
    text = ' '.join(words)
    
    topics = {
        'политика': ['иран', 'китай', 'россия', 'сша', 'украина', 'трамп', 'байден',
                    'израиль', 'палестина', 'нато', 'война', 'конфликт', 'санкции',
                    'выборы', 'президент', 'парламент', 'правительство'],
        
        'экономика': ['нефть', 'газ', 'экономика', 'рынок', 'биржа', 'доллар', 'кризис',
                     'инфляция', 'банк', 'инвестиции', 'бизнес', 'компания'],
        
        'наука': ['наука', 'исследование', 'ученые', 'космос', 'ген', 'мозг', 'климат',
                 'открытие', 'лаборатория', 'эксперимент'],
        
        'технологии': ['ai', 'ии', 'технологии', 'робот', 'цифровой', 'интернет',
                      'гаджет', 'смартфон', 'программ', 'приложение'],
        
        'общество': ['общество', 'люди', 'культура', 'школа', 'университет', 'медицина',
                    'демография', 'миграция', 'город'],
        
        'культура': ['фильм', 'кино', 'книга', 'литература', 'музыка', 'альбом',
                    'выставка', 'театр', 'художник', 'режиссер'],
        
        'спорт': ['спорт', 'футбол', 'чемпионат', 'олимпиада', 'турнир',
                 'матч', 'игрок', 'рекорд'],
        
        'экология': ['экология', 'климат', 'животные', 'природа', 'загрязнение',
                    'вымирание', 'зеленый'],
        
        'здоровье': ['здоровье', 'медицина', 'болезнь', 'лечение', 'вакцина',
                    'больница', 'врач', 'пациент'],
        
        'странное': ['странно', 'необычно', 'удивительно', 'wtf', 'феномен',
                    'мистика', 'паранормально']
    }
    
    for category, keywords in topics.items():
        for keyword in keywords:
            if keyword in text:
                return category
    
    return 'разное'

# ========== БАЛАНСИРОВКА ТЕМ ==========

def balance_groups(groups):
    """Разбавляет темы для разнообразия"""
    topics_count = {}
    selected = []
    
    for group in groups[:15]:  # смотрим топ-15 групп
        topic = extract_topic(group[0]['title'])
        current = topics_count.get(topic, 0)
        
        # Лимиты на тему
        limits = {
            'политика': 3,
            'экономика': 2,
            'наука': 1,
            'технологии': 1,
            'общество': 1,
            'культура': 1,
            'спорт': 1,
            'экология': 1,
            'здоровье': 1,
            'странное': 1,
            'разное': 2
        }
        
        if current < limits.get(topic, 1):
            selected.append(group)
            topics_count[topic] = current + 1
            print(f"⚖️ Добавлена тема {topic} (всего {topics_count[topic]})")
    
    return selected

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
    
    return min(score, 100)

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
    
    # Проверяем, сколько ПОСТОВ реально опубликовано сегодня
    today = datetime.now().strftime("%Y-%m-%d")
    stats = load_stats()
    today_posts = stats.get('days', {}).get(today, {}).get('posts', [])
    
    # Считаем посты на эту тему сегодня
    topic_posts_today = [p for p in today_posts if p.get('topic') == topic]
    
    # Если уже есть 2 поста на тему сегодня - пропускаем
    if len(topic_posts_today) >= 2:
        print(f"⏭️ Уже 2 поста по {topic} сегодня")
        return False
    
    # Если был пост меньше 4 часов назад - пропускаем
    if topic_posts_today:
        last_post = topic_posts_today[-1]
        last_time = datetime.fromisoformat(last_post['time'])
        hours_since = (datetime.now() - last_time).seconds / 3600
        
        if hours_since < 4:
            print(f"⏭️ Последний пост по {topic} был {hours_since:.1f}ч назад")
            return False
    
    return True
    
    last_post = recent[-1]
    last_time = datetime.fromisoformat(last_post['time'])
    hours_since = (datetime.now() - last_time).seconds / 3600
    
    if hours_since > 4:
        print(f"🔄 Прошло {hours_since:.1f}ч, публикуем {topic}")
        return True
    
    print(f"⏭️ Пропускаем {topic} (было {hours_since:.1f}ч назад)")
    return False

# ========== ОЧЕРЕДЬ ПУБЛИКАЦИЙ ==========

def add_to_queue(group, priority, topic):
    """Добавляет пост в очередь"""
    queue = load_queue()
    
    saved_group = []
    for item in group[:3]:
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
    
    queue.sort(key=lambda x: x['priority'], reverse=True)
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
    
    all_news = fetch_all_news()
    if not all_news:
        print("❌ Нет новостей")
        await process_queue()
        return
    
    new_news = filter_new_news(all_news, posted)
    print(f"📰 Новых: {len(new_news)}")
    
    if len(new_news) < 3:
        print("⏸️ Мало новых новостей")
        await process_queue()
        return
    
    groups = group_similar_news(new_news)
    
    if not groups:
        print("❌ Нет групп")
        await process_queue()
        return
    
    # Балансируем темы
    balanced_groups = balance_groups(groups)
    print(f"⚖️ После балансировки: {len(balanced_groups)} групп")
    
    added_to_queue = 0
    for i, group in enumerate(balanced_groups[:10]):
        topic = extract_topic(group[0]['title'])
        priority = calculate_priority(group)
        
        if should_post(group, stats['days'][today]['posts'], topic):
            add_to_queue(group, priority, topic)
            added_to_queue += 1
            print(f"📥 В очередь [{i+1}]: {topic} (приоритет {priority}, {len(group)} источников)")
    
    print(f"📦 Добавлено в очередь: {added_to_queue}")
    
    await process_queue()
    
    stats['total_posts'] = stats['days'][today]['count']
    save_stats(stats)
    
    # Статистика дня
    topics_today = {}
    for post in stats['days'][today]['posts']:
        topic = post.get('topic', 'разное')
        topics_today[topic] = topics_today.get(topic, 0) + 1
    
    print(f"📊 Статистика дня: {topics_today}")

async def process_queue():
    """Обрабатывает очередь публикаций"""
    queue = load_queue()
    
    if not queue:
        print("📭 Очередь пуста")
        return
    
    print(f"📋 В очереди: {len(queue)} постов")
    
    next_post = get_next_from_queue()
    if not next_post:
        return
    
    print(f"📤 Публикую из очереди: {next_post['topic']} (приоритет {next_post['priority']})")
    
    group = []
    for item_data in next_post['group']:
        group.append(NewsItem(item_data))
    
    post = analyze_story_group(group)
    
    if post and len(post) > 50:
        await publish_to_channel(post)
        
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
    print("🚀 WORLD AI NEWS — РАЗНООБРАЗНАЯ ВЕРСИЯ")
    print(f"⏰ Интервал: {POST_INTERVAL_MINUTES} минут")
    print("✅ 10 категорий новостей")
    print("✅ Баланс тем (политика не доминирует)")
    print("✅ Контроль повторов")
    print("✅ Умные приоритеты")
    print("✅ Статистика по темам\n")
    
    queue = load_queue()
    fresh_queue = []
    now = datetime.now()
    for item in queue:
        try:
            added = datetime.fromisoformat(item['time_added'])
            if (now - added).seconds < 3600 * 24:
                fresh_queue.append(item)
        except:
            pass
    save_queue(fresh_queue)
    
    print(f"📦 Очередь очищена, осталось: {len(fresh_queue)} постов\n")
    
    scheduled_job()
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(scheduled_job)
    schedule.every(15).minutes.do(lambda: asyncio.run(process_queue()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()