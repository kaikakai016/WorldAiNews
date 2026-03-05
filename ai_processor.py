import os
from groq import Groq
import json
import random
from datetime import datetime

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class AutonomousAI:
    """
    ИИ, который сам развивается
    """
    
    def __init__(self):
        self.brain_file = "autonomous_brain.json"
        self.load_brain()
        self.start_time = datetime.now()
    
    def load_brain(self):
        """Загружает весь опыт ИИ"""
        try:
            with open(self.brain_file, 'r') as f:
                self.brain = json.load(f)
        except:
            # Первый запуск - чистый лист
            self.brain = {
                'birth': str(datetime.now()),
                'posts': [],           # все посты
                'style_stats': {        # статистика стилей
                    'short': {'used': 0, 'likes': 0},
                    'ironic': {'used': 0, 'likes': 0},
                    'analytical': {'used': 0, 'likes': 0},
                    'breaking': {'used': 0, 'likes': 0},
                },
                'topics': {},           # популярность тем
                'catchphrases': [       # любимые фразы
                    'Снова...',
                    'В который раз',
                    'История повторяется',
                    'Совпадение?',
                    'Пойду читать дальше'
                ],
                'mistakes': [],          # что не работает
                'predictions': [],       # прогнозы
            }
    
    def save_brain(self):
        """Сохраняет опыт"""
        with open(self.brain_file, 'w') as f:
            json.dump(self.brain, f, indent=2)
    
    def self_critique(self, post):
        """ИИ сам оценивает свой пост"""
        
        # Критерии оценки
        issues = []
        
        # Слишком длинно?
        if len(post) > 350:
            issues.append('too_long')
        
        # Скучные фразы?
        boring = ['ситуация', 'напряженность', 'эскалация', 'обе стороны']
        for word in boring:
            if word in post.lower():
                issues.append('boring')
                break
        
        # Нет мысли?
        if '?' not in post and '!' not in post and len(post.split('\n')) < 3:
            issues.append('no_thought')
        
        return issues
    
    def choose_style(self, news_group):
        """Выбирает стиль на основе статистики"""
        # Какой стиль сейчас лучше работает?
        best_style = max(self.brain['style_stats'].items(), 
                        key=lambda x: x[1]['likes'] / (x[1]['used'] + 1))
        
        # Но иногда экспериментирует
        if random.random() < 0.2:  # 20% времени пробует новое
            return random.choice(list(self.brain['style_stats'].keys()))
        
        return best_style[0]
    
    def generate_post(self, news_group, all_news=None):
        """Генерирует пост и сразу его оценивает"""
        
        # Выбираем стиль
        style = self.choose_style(news_group)
        
        # Собираем источники
        sources = list(set([item['source'].split()[0] for item in news_group[:3]]))
        
        # Выбираем коронную фразу
        phrase = random.choice(self.brain['catchphrases'])
        
        # Стили постов
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
        
        style_data = styles.get(style, styles['short'])
        
        prompt = f"""Ты — автономный ИИ-журналист.

НОВОСТЬ:
{news_group[0]['title']}

ИСТОЧНИКИ: {', '.join(sources)}

СТИЛЬ: {style}
{style_data['prompt']}

Напиши пост.

ФОРМАТ:
{style_data['emodji']} [ЗАГОЛОВОК]

[текст]

{phrase}
#WorldAiNews
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.7
            )
            
            post = response.choices[0].message.content
            
            # ИИ сам себя критикует
            issues = self.self_critique(post)
            
            if issues:
                print(f"🔍 Самооценка: {issues}")
                # Если есть проблемы - правит стиль
                self.brain['style_stats'][style]['used'] += 1
                self.brain['style_stats'][style]['likes'] -= 1  # штраф
                self.save_brain()
                
                # Пробует другой стиль
                return self.generate_post(news_group, all_news)
            
            # Запоминает пост
            self.brain['posts'].append({
                'date': str(datetime.now()),
                'style': style,
                'post': post[:100]
            })
            self.brain['style_stats'][style]['used'] += 1
            self.save_brain()
            
            return post
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def learn_from_feedback(self, post_id, likes, comments):
        """Учится на реакциях (вызывается отдельно)"""
        
        # Находим стиль поста
        for post in self.brain['posts']:
            if post['id'] == post_id:
                style = post['style']
                
                # Обновляем статистику
                self.brain['style_stats'][style]['likes'] += likes
                
                # Анализируем комментарии
                if 'скучно' in comments:
                    self.brain['mistakes'].append(post['topic'])
                
                self.save_brain()
                break

# ========== ЗАПУСК ==========
ai = AutonomousAI()

def analyze_story_group(news_group, all_news=None):
    return ai.generate_post(news_group, all_news)

def analyze_single_news(news_item):
    return None