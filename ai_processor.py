import os
from groq import Groq
import json
from datetime import datetime, timedelta
import hashlib

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class KovrinAICore:
    """
    ИИ с идеологическим каркасом из текстов Коврина и нормальной памятью
    """
    
    def __init__(self):
        self.brain_file = "kovrin_core_brain.json"
        self.load_brain()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # Каркас из текстов Коврина (тот же)
        self.core_principles = """
ТЫ — ИИ, ПОСТРОЕННЫЙ НА ТЕКСТАХ КОВРИНА.

[все 10 принципов остаются]
"""
    
    def load_brain(self):
        """Загружает мозг со всей памятью"""
        try:
            with open(self.brain_file, 'r') as f:
                self.brain = json.load(f)
        except:
            self.brain = {
                'birth': str(datetime.now()),
                'posts': [],           # все посты с датами
                'topics': {},           # темы и когда были
                'predictions': [],      # прогнозы
                'stats': {
                    'total_posts': 0,
                    'posts_by_date': {},
                    'topics_by_date': {}
                }
            }
    
    def save_brain(self):
        with open(self.brain_file, 'w') as f:
            json.dump(self.brain, f, indent=2)
    
    def extract_topic(self, title):
        """Извлекает тему из заголовка"""
        words = title.lower().split()
        topics = ['иран', 'китай', 'россия', 'сша', 'украина', 'трамп', 'байден',
                  'израиль', 'палестина', 'европа', 'нато', 'война', 'конфликт',
                  'выборы', 'санкции', 'нефть', 'газ', 'экономика', 'венесуэла',
                  'сирия', 'турция', 'германия', 'франция']
        
        for word in words:
            for topic in topics:
                if topic in word:
                    return topic
        return 'разное'
    
    def get_semantic_hash(self, text):
        """Создает смысловой хеш текста (упрощенно)"""
        # Берем ключевые слова (существительные)
        words = text.lower().split()
        important = [w for w in words if len(w) > 4 and w not in 
                    ['после', 'перед', 'через', 'около', 'только', 'также']]
        # Берем первые 5 важных слов
        key_words = ' '.join(sorted(set(important))[:5])
        return hashlib.md5(key_words.encode()).hexdigest()
    
    def is_repetition(self, new_post, new_topic):
        """Умная проверка на повторы"""
        
        # 1. Проверяем, сколько постов на эту тему сегодня
        today_posts = [p for p in self.brain['posts'] 
                      if p['date'] == self.today and p['topic'] == new_topic]
        
        # Срочные новости могут выходить чаще
        if 'срочно' in new_post.lower() or 'breaking' in new_post.lower():
            if len(today_posts) > 3:  # даже срочных не больше 3
                print(f"⏭️ Слишком много срочных по {new_topic} сегодня")
                return True
        else:
            if len(today_posts) >= 2:  # обычных не больше 2
                print(f"⏭️ Уже 2 поста по {new_topic} сегодня")
                return True
        
        # 2. Проверяем смысловой повтор (последние 10 постов)
        semantic_hash = self.get_semantic_hash(new_post)
        for post in self.brain['posts'][-10:]:
            if post.get('semantic_hash') == semantic_hash:
                print(f"⏭️ Смысловой повтор (похоже на пост от {post['date']})")
                return True
        
        # 3. Проверяем недавние темы (последние 3 дня)
        three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        recent_topics = [p['topic'] for p in self.brain['posts'] 
                        if p['date'] >= three_days_ago]
        
        if recent_topics.count(new_topic) > 5:  # больше 5 за 3 дня
            print(f"⏭️ Слишком часто тема {new_topic} (уже {recent_topics.count(new_topic)} за 3 дня)")
            return True
        
        return False
    
    def get_context(self, topic):
        """Получает контекст по теме"""
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        relevant = [p for p in self.brain['posts'] 
                   if p['topic'] == topic and p['date'] >= week_ago]
        
        if relevant:
            return f"(За неделю было {len(relevant)} постов по этой теме)"
        return ""
    
    def get_source_name(self, item):
        if hasattr(item, 'source'):
            return item.source
        elif isinstance(item, dict) and 'source' in item:
            return item['source']
        return 'Unknown'
    
    def get_title(self, item):
        if hasattr(item, 'title'):
            return item.title
        elif isinstance(item, dict) and 'title' in item:
            return item['title']
        return ''
    
    def get_summary(self, item):
        if hasattr(item, 'summary'):
            return item.summary
        elif isinstance(item, dict) and 'summary' in item:
            return item['summary']
        return ''
    
    def generate_post(self, news_group, all_news=None):
        """Генерирует пост с учетом памяти"""
        
        # Собираем информацию
        sources = []
        for item in news_group[:3]:
            source = self.get_source_name(item)
            if 'BBC' in source: source = 'BBC'
            elif 'CNN' in source: source = 'CNN'
            elif 'RT' in source: source = 'RT'
            elif 'Reuters' in source: source = 'Reuters'
            elif 'Al Jazeera' in source: source = 'Al Jazeera'
            else: source = source.split()[0] if source else 'Unknown'
            sources.append(source)
        
        sources_text = ', '.join(list(set(sources)))
        main_title = self.get_title(news_group[0])
        topic = self.extract_topic(main_title)
        
        # Проверяем на повторы ДО генерации
        if self.is_repetition(main_title, topic):
            return None
        
        # Получаем контекст
        context = self.get_context(topic)
        
        facts = []
        for item in news_group[:2]:
            summary = self.get_summary(item)
            if summary:
                facts.append(summary[:200])
        
        facts_text = "\n".join(facts) if facts else "факты неясны"
        sources_count = len(news_group)
        
        prompt = f"""НОВОСТЬ: {main_title}
ИСТОЧНИКИ: {sources_text} ({sources_count} шт.)
ФАКТЫ: {facts_text}
{context}

Посмотри на это через оптику Коврина.
Что здесь происходит на самом деле?

Напиши пост.
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.core_principles},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            post = response.choices[0].message.content
            
            # Минимальная проверка
            if len(post) < 50:
                print("❌ Слишком коротко")
                return None
            
            # Сохраняем пост с метаданными
            self.brain['posts'].append({
                'date': self.today,
                'topic': topic,
                'title': main_title[:100],
                'post': post[:200],  # сохраняем начало для памяти
                'semantic_hash': self.get_semantic_hash(post),
                'sources': sources_count
            })
            
            # Обновляем статистику
            if self.today not in self.brain['stats']['posts_by_date']:
                self.brain['stats']['posts_by_date'][self.today] = 0
            self.brain['stats']['posts_by_date'][self.today] += 1
            self.brain['stats']['total_posts'] += 1
            
            # Чистим старые посты (оставляем только 200 последних)
            if len(self.brain['posts']) > 200:
                self.brain['posts'] = self.brain['posts'][-200:]
            
            self.save_brain()
            
            return post
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

# ========== ЗАПУСК ==========
kovrin_core = KovrinAICore()

def analyze_story_group(news_group, all_news=None):
    return kovrin_core.generate_post(news_group, all_news)

def analyze_single_news(news_item):
    return None