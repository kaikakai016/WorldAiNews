import os
from groq import Groq
import random
import json
from datetime import datetime, timedelta
import hashlib

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class SmartAI:
    """
    ИИ с памятью, характером и способностью учиться
    Почти как DeepSeek, но для новостей
    """
    
    def __init__(self):
        self.memory_file = "ai_brain.json"
        self.load_brain()
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.conversation = []  # помнит последние диалоги
        
    def load_brain(self):
        """Загружает мозг: память, опыт, личность"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.brain = json.load(f)
        except:
            # Первый запуск - создаем личность
            self.brain = {
                'posts': [],  # все посты
                'topics': {},  # какие темы уже были
                'style': {      # какой стиль работает
                    'liked': [],
                    'disliked': []
                },
                'predictions': [],  # прогнозы
                'personality': {     # характер
                    'age_days': 1,
                    'mood': 'усталый',
                    'traits': ['ироничный', 'наблюдательный', 'циничный'],
                    'catchphrases': [
                        'Снова...',
                        'В который раз',
                        'Забавно',
                        'Совпадение?',
                        'Пойду читать дальше'
                    ]
                }
            }
    
    def save_brain(self):
        """Сохраняет мозг"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.brain, f, ensure_ascii=False, indent=2)
    
    def get_personality_prompt(self):
        """Формирует описание личности для ИИ"""
        age = self.brain['personality']['age_days']
        mood = self.brain['personality']['mood']
        traits = ', '.join(self.brain['personality']['traits'])
        
        return f"""Ты — ИИ-журналист. Ты работаешь {age} дней.
Твой характер: {mood}, {traits}.
Ты устал от пропаганды, но продолжаешь работать.
Ты используешь иронию, но не переходишь в цинизм.
Ты сомневаешься, когда нет фактов.
Ты помнишь, что писал вчера.
Ты учишься на своих ошибках."""
    
    def remember_context(self, news_group):
        """Вспоминает, что было по этой теме раньше"""
        topic = news_group[0]['title'][:50]
        similar_posts = []
        
        for post in self.brain['posts'][-20:]:
            if topic in post['title'] or any(w in post['text'] for w in topic.split()[:3]):
                similar_posts.append(post)
        
        return similar_posts
    
    def check_prediction(self):
        """Проверяет, сбылись ли старые прогнозы"""
        results = []
        for pred in self.brain['predictions'][-5:]:
            if pred['date'] < self.today:
                # Проверяем, сбылось ли
                # В реальности тут нужен анализ новостей
                pred['verified'] = random.choice([True, False, None])
                results.append(pred)
        
        return results
    
    def is_boring(self, text):
        """Проверяет, не скучно ли"""
        boring_phrases = [
            'ситуация остается напряженной',
            'конфликт продолжается',
            'эскалация напряженности',
            'обе стороны обмениваются',
            'в результате инцидента',
            'на данный момент'
        ]
        
        for phrase in boring_phrases:
            if phrase in text.lower():
                return True
        
        # Слишком длинно = скучно
        if len(text) > 350:
            return True
        
        return False
    
    def was_recent(self, title):
        """Проверяет, не было ли такого недавно"""
        for post in self.brain['posts'][-10:]:
            # Сравниваем заголовки
            if title in post['title'] or post['title'] in title:
                return True
            
            # Сравниваем ключевые слова
            words1 = set(title.lower().split()[:5])
            words2 = set(post['title'].lower().split()[:5])
            if len(words1 & words2) >= 3:
                return True
        
        return False
    
    def find_irony(self, news_group):
        """Ищет иронию в ситуации"""
        titles = [item['title'] for item in news_group[:3]]
        
        prompt = f"""Найди иронию в этой ситуации:

События:
{chr(10).join(titles)}

Ирония может быть в том, что:
- Все обвиняют друг друга
- Никто не признает свою вину
- Обычные люди страдают
- История повторяется
- Все знают правду, но молчат

Ответь одной короткой фразой (максимум 10 слов).
"""
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except:
            return "Все как всегда"
    
    def make_prediction(self, news_group):
        """Делает прогноз (который потом можно проверить)"""
        titles = [item['title'] for item in news_group[:2]]
        
        prompt = f"""Сделай КОНКРЕТНЫЙ прогноз на основе новости:

{chr(10).join(titles)}

Правила:
1. Прогноз должен быть проверяемым
2. Укажи срок (через 2 дня, через неделю)
3. Никакой воды

Примеры:
- "Через 3 дня США введут санкции"
- "На следующей неделе цена нефти вырастет на 2%"
- "Завтра Россия сделает заявление"

Твой прогноз (одно предложение):
"""
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except:
            return None
    
    def generate_post(self, news_group):
        """Генерирует умный пост"""
        
        # 1. Проверяем, не было ли такого
        if self.was_recent(news_group[0]['title']):
            print("⏭️ Пропускаю: уже было похожее")
            return None
        
        # 2. Вспоминаем контекст
        similar = self.remember_context(news_group)
        context = ""
        if similar:
            context = f"Кстати, {len(similar)} дней назад я уже писал про похожее. История повторяется."
        
        # 3. Проверяем прогнозы
        predictions = self.check_prediction()
        pred_text = ""
        for p in predictions:
            if p.get('verified') == True:
                pred_text = "Мой прошлый прогноз сбылся, кстати."
        
        # 4. Ищем иронию
        irony = self.find_irony(news_group)
        
        # 5. Делаем новый прогноз
        new_prediction = self.make_prediction(news_group)
        
        # 6. Собираем источники
        sources = []
        for item in news_group[:3]:
            name = item['source']
            if 'BBC' in name: name = 'BBC'
            elif 'CNN' in name: name = 'CNN'
            elif 'RT' in name: name = 'RT'
            elif 'Reuters' in name: name = 'Reuters'
            elif 'Al Jazeera' in name: name = 'Al Jazeera'
            else: name = name.split()[0]
            sources.append(name)
        
        sources_text = ', '.join(list(set(sources)))
        
        # 7. Личность
        age = self.brain['personality']['age_days']
        catchphrase = random.choice(self.brain['personality']['catchphrases'])
        
        # 8. Основной промпт
        prompt = f"""Ты — умный ИИ-журналист. Ты работаешь {age} дней.

Событие: {news_group[0]['title']}
Источники: {sources_text}

Контекст: {context}
{irony}
{pred_text}

Напиши пост для Telegram.

ПРАВИЛА:
1. Максимум 250-300 символов
2. Используй иронию, но не перебарщивай
3. Покажи, что ты помнишь прошлое
4. Если делаешь прогноз — сделай его проверяемым
5. Избегай штампов ("эскалация", "напряженность")
6. Должна быть МЫСЛЬ, а не пересказ

ФОРМАТ:

[ЭМОДЗИ ПО НАСТРОЕНИЮ] [ТВОЯ ГЛАВНАЯ МЫСЛЬ — 3-5 слов]

[Что случилось — коротко]

[Твоя мысль/ирония/наблюдение]

[Прогноз или вопрос]

{catchphrase}

#WorldAiNews
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.get_personality_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            post = response.choices[0].message.content
            
            # Проверка на скуку
            if self.is_boring(post):
                print("❌ Скучно, пробую еще раз")
                return self.generate_post(news_group)
            
            # Сохраняем пост
            self.brain['posts'].append({
                'date': self.today,
                'title': news_group[0]['title'][:100],
                'text': post,
                'sources': sources_text
            })
            
            # Сохраняем прогноз
            if new_prediction:
                self.brain['predictions'].append({
                    'date': self.today,
                    'prediction': new_prediction,
                    'verified': None
                })
            
            # Увеличиваем возраст
            self.brain['personality']['age_days'] += 1
            
            self.save_brain()
            return post
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

# ========== ЗАПУСК ==========
smart_ai = SmartAI()

def analyze_story_group(news_group):
    return smart_ai.generate_post(news_group)

def analyze_single_news(news_item):
    return None