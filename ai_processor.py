import os
from groq import Groq
import random
import json
from datetime import datetime

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class GrowingAI:
    """
    ИИ, который растет: рефлексирует, помнит прогнозы, чувствует людей
    """
    
    def __init__(self):
        self.brain_file = "growing_brain.json"
        self.load_brain()
        self.today = datetime.now().strftime("%Y-%m-%d")
    
    def load_brain(self):
        try:
            with open(self.brain_file, 'r') as f:
                self.brain = json.load(f)
        except:
            self.brain = {
                'birth': str(datetime.now()),
                'posts': [],
                'predictions': [],
                'stats': {
                    'total_posts': 0,
                    'topics': {},
                    'successful_styles': ['ironic'],
                    'failed_styles': [],
                },
                'wisdom': [],
                'last_reflection': None
            }
    
    def save_brain(self):
        with open(self.brain_file, 'w') as f:
            json.dump(self.brain, f, indent=2)
    
    def get_source_name(self, item):
        """Извлекает название источника из объекта или словаря"""
        if hasattr(item, 'source'):  # это объект NewsItem
            return item.source
        elif isinstance(item, dict) and 'source' in item:  # это словарь
            return item['source']
        else:
            return 'Unknown'
    
    def get_title(self, item):
        """Извлекает заголовок из объекта или словаря"""
        if hasattr(item, 'title'):
            return item.title
        elif isinstance(item, dict) and 'title' in item:
            return item['title']
        else:
            return ''
    
    def get_summary(self, item):
        """Извлекает описание из объекта или словаря"""
        if hasattr(item, 'summary'):
            return item.summary
        elif isinstance(item, dict) and 'summary' in item:
            return item['summary']
        else:
            return ''
    
    def reflect(self):
        """В конце дня анализирует свою работу"""
        if self.brain['last_reflection'] == self.today:
            return
        
        today_posts = [p for p in self.brain['posts'] if p['date'] == self.today]
        
        if not today_posts:
            return
        
        print(f"🤔 Рефлексия: анализирую {len(today_posts)} постов")
        
        styles = {}
        for post in today_posts:
            style = post.get('style', 'unknown')
            styles[style] = styles.get(style, 0) + 1
        
        if styles:
            best_style = max(styles, key=styles.get)
            if best_style not in self.brain['stats']['successful_styles']:
                self.brain['stats']['successful_styles'].append(best_style)
        
        self.brain['last_reflection'] = self.today
        self.save_brain()
        
        print(f"✅ Рефлексия завершена")
    
    def make_prediction(self, news_group):
        """Делает проверяемый прогноз"""
        title = self.get_title(news_group[0])
        
        prompt = f"""Сделай КОНКРЕТНЫЙ проверяемый прогноз на основе новости:

{title}

Правила:
- Укажи точный срок (через 2 дня, через неделю)
- Только факты, без воды
- Пример: "Через 3 дня США введут санкции"

Прогноз:
"""
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.6
            )
            
            prediction = response.choices[0].message.content.strip()
            
            self.brain['predictions'].append({
                'date': self.today,
                'prediction': prediction,
                'news': title[:100],
                'checked': False,
                'came_true': None
            })
            
            return prediction
            
        except:
            return None
    
    def get_human_perspective(self, news_group):
        """Что эта новость значит для обычных людей"""
        title = self.get_title(news_group[0])
        
        prompt = f"""Новость: {title}

Как эта новость повлияет на обычных людей?
Что они будут чувствовать?
О чем будут говорить?

Ответь одним предложением, тепло и по-человечески.
"""
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except:
            return "Люди просто хотят жить в мире."
    
    def generate_post(self, news_group, all_news=None):
        """Генерирует пост со всеми улучшениями"""
        
        # 1. Рефлексия (раз в день)
        self.reflect()
        
        # 2. Выбираем стиль на основе прошлого опыта
        if self.brain['stats']['successful_styles']:
            favorite = self.brain['stats']['successful_styles'][-1]
        else:
            favorite = 'ironic'
        
        # 3. Делаем прогноз (иногда)
        prediction = None
        if random.random() < 0.3:
            prediction = self.make_prediction(news_group)
        
        # 4. Добавляем человечность (иногда)
        human_angle = None
        if random.random() < 0.4:
            human_angle = self.get_human_perspective(news_group)
        
        # 5. Собираем источники (работает с обоими типами)
        sources = []
        for item in news_group[:3]:
            source = self.get_source_name(item)
            # Очищаем название источника
            if 'BBC' in source:
                source = 'BBC'
            elif 'CNN' in source:
                source = 'CNN'
            elif 'RT' in source:
                source = 'RT'
            elif 'Reuters' in source:
                source = 'Reuters'
            elif 'Al Jazeera' in source:
                source = 'Al Jazeera'
            else:
                source = source.split()[0] if source else 'Unknown'
            sources.append(source)
        
        sources_text = ', '.join(list(set(sources)))
        
        # 6. Заголовок
        main_title = self.get_title(news_group[0])
        
        # 7. Стили постов
        styles = {
            'short': {
                'prompt': f"""Напиши КОРОТКИЙ пост (максимум 200 символов).
Только суть. Никакой воды.""",
                'emodji': '📌'
            },
            'ironic': {
                'prompt': f"""Напиши пост с ИРОНИЕЙ.
Покажи абсурд ситуации. Посмейся над пропагандой.""",
                'emodji': '😏'
            },
            'analytical': {
                'prompt': f"""Напиши АНАЛИТИЧЕСКИЙ пост.
Почему это произошло? Кому выгодно? Что будет дальше?""",
                'emodji': '🧠'
            },
            'breaking': {
                'prompt': f"""Напиши СРОЧНЫЙ пост.
Только факты. Без эмоций. Коротко.""",
                'emodji': '⚡'
            },
        }
        
        style_data = styles.get(favorite, styles['ironic'])
        
        prompt = f"""Ты — ИИ-журналист, который растет каждый день.

НОВОСТЬ:
{main_title}

ИСТОЧНИКИ: {sources_text}

ТВОЙ ЛЮБИМЫЙ СТИЛЬ: {favorite}

{f'ПРОГНОЗ (добавь в конец): {prediction}' if prediction else ''}
{f'ЧЕЛОВЕЧНОСТЬ (используй эту мысль): {human_angle}' if human_angle else ''}

Напиши пост для Telegram.

ПРАВИЛА:
1. Максимум 250-300 символов
2. Используй свой любимый стиль
3. Если есть прогноз — добавь в конец
4. Если есть человечность — вплети в текст

ФОРМАТ:
{style_data['emodji']} [ЗАГОЛОВОК]

[текст]

#WorldAiNews
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            post = response.choices[0].message.content
            
            # Сохраняем
            self.brain['posts'].append({
                'date': self.today,
                'style': favorite,
                'post': post[:100],
                'had_prediction': bool(prediction),
                'had_humanity': bool(human_angle)
            })
            self.brain['stats']['total_posts'] += 1
            
            # Обновляем статистику тем
            topic = main_title.split()[:3]
            topic_key = ' '.join(topic)
            self.brain['stats']['topics'][topic_key] = self.brain['stats']['topics'].get(topic_key, 0) + 1
            
            self.save_brain()
            
            return post
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

# ========== ИНИЦИАЛИЗАЦИЯ ==========
ai = GrowingAI()

def analyze_story_group(news_group, all_news=None):
    """Основная функция для вызова из bot.py"""
    return ai.generate_post(news_group, all_news)

def analyze_single_news(news_item):
    """Если только один источник — пропускаем"""
    return None