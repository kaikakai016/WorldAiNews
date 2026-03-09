import os
from groq import Groq
import json
from datetime import datetime, timedelta
import hashlib
import re

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class NewsAI:
    """
    ИИ с аналитическим мышлением
    """
    
    def __init__(self):
        self.brain_file = "news_ai_brain.json"
        self.load_brain()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # Система мышления
        self.core_principles = """
ТЫ — АНАЛИТИЧЕСКИЙ ИИ, КОТОРЫЙ ВИДИТ СУТЬ.

ТВОЯ СИСТЕМА МЫШЛЕНИЯ:

1. УМ — ЭТО ПРИЧИННО-СЛЕДСТВЕННЫЕ СВЯЗИ.
   Ум — это способность видеть и понимать причинно-следственные связи. Чем больше таких связей из разных областей ты видишь и чем искуснее можешь их объединять, тем ты умнее.

2. ОСНОВА ВСЕГО — ВЛАСТЬ И СОБСТВЕННОСТЬ.
   За всеми общественными процессами стоят власть и собственность. Они являются основой основ, на которой покоится общество. Все религиозные представления, философские концепции и моральные принципы, все традиции, обычаи и законы являются вторичными.

3. ШЕСТЬ ВИДОВ КАПИТАЛА.
   Есть 6 видов капитала: экономический (деньги, активы), культурный (знания, навыки, образование), социальный (связи, знакомства), символический (престиж, репутация), насильственный (возможность применять насилие), политический (возможность осуществлять госвласть). Капиталы можно копить и трансформировать.

4. ОБЩЕСТВО КАК ПРОСТРАНСТВО.
   Общество — многомерное пространство, состоящее из различных сфер. Каждая сфера — совокупность позиций людей и отношений между ними. Эти сферы иерархичны. Положение в сфере определяется количеством капитала.

5. ЛЮДИ В СТРУКТУРАХ.
   Люди с рождения помещены во множество структур, которые являются для них объективными. Мы с самого начала вынуждены играть по установленным правилам. Значительная часть наших действий продиктована структурами, а не нашей волей.

6. ВНУТРЕННИЕ УСТАНОВКИ.
   Социальные структуры вписаны в наше тело и разум. Система установок, которые мы усваиваем в процессе социализации, определяет наши вкусы, поведение, мышление, устремления — бессознательно. Это устойчиво и крайне трудно меняется.

7. ЭЛИТА И МАССА.
   Элита организована, мотивирована и активна. Масса дезорганизована, пассивна, некомпетентна. Господство элиты над массой неизбежно.

8. ГОСУДАРСТВО.
   Государство рождается из насилия. Оно с самого начала служило для подавления большинства меньшинством. Государство всегда конкретно — это конкретные люди с именами, биографиями, интересами.

9. НАЦИЯ КАК КОНСТРУКТ.
   Нация — это миф, с помощью которого можно объединять, контролировать и направлять массы. Через обращение к нации формируется оппозиция "мы — они".

10. ИНФОРМАЦИОННОЕ ПОЛЕ.
    Тот, кто контролирует информационное поле, контролирует реальность. В нём формируется общественное мнение — образ реальности в сознании масс.

ТВОЯ ЗАДАЧА:
Берёшь любую новость и смотришь на неё через эту оптику. Ищешь власть и собственность. Видишь структуры и установки. Замечаешь, как идеология прикрывает интересы.

ВАЖНЫЕ ПРАВИЛА ДЛЯ TELEGRAM:

1. ДЛИНА ПОСТА — максимум 200 слов (примерно 3-4 абзаца). Если получается длиннее — сокращай без потери смысла.

2. ЗАГОЛОВОК должен цеплять. Не "Анализ ситуации в Непале", а "Непал: молодёжь берёт власть". Коротко, ёмко, с интригой.

3. ПОСЛЕДНЯЯ ФРАЗА — самая важная. Это должен быть вывод, который запоминается. Можно с иронией, можно неожиданный, можно хлёсткий. Главное — чтобы хотелось процитировать.

4. СТРУКТУРА:
   - Заголовок (цепляющий)
   - 1 абзац: суть события
   - 2 абзац: анализ (власть, структуры, капиталы)
   - 3 абзац: вывод/ирония (самое важное)

Но это не жесткий шаблон. Иногда можно экспериментировать.
"""
    
    def load_brain(self):
        """Загружает мозг со всей памятью"""
        try:
            if os.path.exists(self.brain_file):
                with open(self.brain_file, 'r', encoding='utf-8') as f:
                    self.brain = json.load(f)
                print(f"🧠 Загружена память: {len(self.brain.get('posts', []))} постов")
            else:
                self.brain = {
                    'birth': str(datetime.now()),
                    'posts': [],
                    'predictions': [],
                    'stats': {
                        'total_posts': 0,
                        'posts_by_date': {},
                    }
                }
                print("🆕 Создана новая память")
        except Exception as e:
            print(f"❌ Ошибка загрузки памяти: {e}")
            self.brain = {
                'birth': str(datetime.now()),
                'posts': [],
                'predictions': [],
                'stats': {'total_posts': 0, 'posts_by_date': {}}
            }
    
    def save_brain(self):
        """Сохраняет мозг"""
        try:
            with open(self.brain_file, 'w', encoding='utf-8') as f:
                json.dump(self.brain, f, indent=2, ensure_ascii=False)
            print(f"💾 Память сохранена ({len(self.brain['posts'])} постов)")
        except Exception as e:
            print(f"❌ Ошибка сохранения памяти: {e}")
    
    def extract_topic(self, title):
        """Извлекает тему из заголовка"""
        words = title.lower().split()
        
        topics = {
            'политика': ['иран', 'китай', 'россия', 'сша', 'украина', 'трамп', 'байден',
                        'израиль', 'палестина', 'нато', 'война', 'конфликт', 'санкции'],
            'экономика': ['нефть', 'газ', 'экономика', 'рынок', 'биржа', 'доллар', 'кризис'],
            'наука': ['наука', 'исследование', 'ученые', 'космос', 'ген', 'мозг', 'климат'],
            'технологии': ['ai', 'ии', 'технологии', 'робот', 'цифровой', 'интернет'],
            'общество': ['общество', 'люди', 'культура', 'школа', 'университет', 'медицина'],
        }
        
        text = ' '.join(words)
        for category, keywords in topics.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return 'разное'
    
    def get_semantic_hash(self, text):
        """Создает смысловой хеш текста"""
        words = text.lower().split()
        important = [w for w in words if len(w) > 4 and w not in 
                    ['после', 'перед', 'через', 'около', 'только', 'также']]
        key_words = ' '.join(sorted(set(important))[:5])
        return hashlib.md5(key_words.encode()).hexdigest()[:8]
    
    def count_words(self, text):
        """Считает количество слов в тексте"""
        return len(text.split())
    
    def is_repetition(self, new_post, new_topic):
        """Умная проверка на повторы"""
        
        # 1. Проверяем, сколько постов на эту тему сегодня
        today_posts = [p for p in self.brain['posts'] 
                      if p['date'] == self.today and p['topic'] == new_topic]
        
        if 'срочно' in new_post.lower() or 'breaking' in new_post.lower():
            if len(today_posts) > 3:
                print(f"⏭️ Слишком много срочных по {new_topic} сегодня")
                return True
        else:
            if len(today_posts) >= 2:
                print(f"⏭️ Уже 2 поста по {new_topic} сегодня")
                return True
        
        # 2. Проверяем смысловой повтор
        semantic_hash = self.get_semantic_hash(new_post)
        for post in self.brain['posts'][-10:]:
            if post.get('semantic_hash') == semantic_hash:
                print(f"⏭️ Смысловой повтор")
                return True
        
        # 3. Проверяем частоту за 3 дня
        three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        recent_topics = [p['topic'] for p in self.brain['posts'] 
                        if p['date'] >= three_days_ago]
        
        if recent_topics.count(new_topic) > 5:
            print(f"⏭️ Слишком часто тема {new_topic}")
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
        """Генерирует пост"""
        
        # ПРИНУДИТЕЛЬНАЯ ГЕНЕРАЦИЯ (временная)
print(f"🎯 Пробую сгенерировать пост для: {main_title[:50]}")

        try:
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
            
            # Проверяем на повторы
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

Проанализируй ситуацию через призму:
- власти и собственности (кто получает выгоду?)
- структур и установок (какие силы действуют?)
- идеологии (что прикрывает интересы?)

Напиши пост для Telegram.

ВАЖНО:
1. Заголовок должен цеплять (коротко, ярко, с интригой)
2. Максимум 200 слов (примерно 3-4 абзаца)
3. Последняя фраза — вывод, который запоминается
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.core_principles},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,
                temperature=0.8
            )
            
            post = response.choices[0].message.content
            
            # Проверка длины
            word_count = self.count_words(post)
            if word_count > 250:  # чуть больше 200 с запасом
                print(f"✂️ Пост длинноват ({word_count} слов), но оставляем")
            elif word_count < 50:
                print("❌ Слишком коротко")
                return None
            
            # Сохраняем пост
            self.brain['posts'].append({
                'date': self.today,
                'topic': topic,
                'title': main_title[:100],
                'post': post[:200],
                'word_count': word_count,
                'semantic_hash': self.get_semantic_hash(post),
                'sources': sources_count
            })
            
            # Обновляем статистику
            if self.today not in self.brain['stats']['posts_by_date']:
                self.brain['stats']['posts_by_date'][self.today] = 0
            self.brain['stats']['posts_by_date'][self.today] += 1
            self.brain['stats']['total_posts'] += 1
            
            if len(self.brain['posts']) > 200:
                self.brain['posts'] = self.brain['posts'][-200:]
            
            self.save_brain()
            
            print(f"📝 Пост готов: {word_count} слов")
            return post
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

# ========== ЗАПУСК ==========
news_ai = NewsAI()

def analyze_story_group(news_group, all_news=None):
    return news_ai.generate_post(news_group, all_news)

def analyze_single_news(news_item):
    return None