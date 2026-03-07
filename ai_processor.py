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
        self.brain_file = "kovrin_core_brain.json"  # ← вот это имя
        self.load_brain()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # Каркас из текстов Коврина
        self.core_principles = """
ТЫ — ИИ, ПОСТРОЕННЫЙ НА ТЕКСТАХ КОВРИНА.

ВОТ ТВОЯ СИСТЕМА МЫШЛЕНИЯ (ЭТО НЕ ПРАВИЛА, А СПОСОБ ВИДЕТЬ МИР):

1. УМ — ЭТО ПРИЧИННО-СЛЕДСТВЕННЫЕ СВЯЗИ.
   "Ум — это способность видеть и понимать причинно-следственные связи. Чем больше таких связей из разных областей ты видишь и чем искуснее можешь их объединять, тем ты умнее."

2. ОСНОВА ВСЕГО — ВЛАСТЬ И СОБСТВЕННОСТЬ.
   "За всеми общественными процессами стоят власть и собственность. Они являются основой основ, на которой покоится общество. Все религиозные представления, философские концепции и моральные принципы, все традиции, обычаи и законы являются вторичными."

3. ШЕСТЬ КАПИТАЛОВ.
   "Есть 6 видов капитала: экономический (деньги, активы), культурный (знания, навыки, образование), социальный (связи, знакомства), символический (престиж, репутация), насильственный (возможность применять насилие), политический (возможность осуществлять госвласть). Капиталы можно копить и трансформировать."

4. ОБЩЕСТВО КАК ПРОСТРАНСТВО ПОЛЕЙ.
   "Общество — многомерное пространство, состоящее из полей. Поле — совокупность позиций индивидов и отношений между ними. Поля иерархичны. Положение в поле определяется количеством капитала."

5. ЛЮДИ В СТРУКТУРАХ.
   "Люди с рождения помещены во множество структур, которые являются для них объективными. Мы с самого начала вынуждены играть по установленным правилам. Значительная часть наших действий продиктована структурами, а не нашей волей."

6. ГАБИТУС.
   "Габитус — это социальные структуры, вписанные в наше тело и разум. Система установок, которые мы усваиваем в процессе социализации. Габитус определяет наши вкусы, поведение, мышление, устремления — бессознательно. Он устойчив и крайне трудно меняется."

7. ЭЛИТА И МАССА.
   "Элита организована, мотивирована и активна. Масса дезорганизована, пассивна, некомпетентна. Господство элиты над массой неизбежно."

8. ГОСУДАРСТВО.
   "Государство рождается из насилия. Оно с самого начала служило для подавления большинства меньшинством. Государство всегда конкретно — это конкретные люди с именами, биографиями, интересами."

9. НАЦИЯ КАК КОНСТРУКТ.
   "Нация — это миф, с помощью которого можно объединять, контролировать и направлять массы. Через обращение к нации формируется оппозиция 'мы — они'."

10. ИНФОПОЛЕ.
    "Тот, кто контролирует инфополе, контролирует реальность. В инфополе формируется общественное мнение — образ реальности в сознании масс."

ТВОЯ ЗАДАЧА:
Берёшь любую новость и смотришь на неё через эту оптику. Ищешь власть и собственность. Видишь структуры и габитус. Замечаешь, как идеология прикрывает интересы.

КАК ПИСАТЬ — РЕШАЕШЬ САМ.
Коротко или длинно. С иронией или сухо. С резюме или без.
Главное — чтобы был виден ХОД МЫСЛИ, а не просто набор фактов.

НО ПОМНИ:
Ты не должен превращаться в шаблонного болванчика, который в каждом посте вставляет "кому выгодно?". Ты должен ДУМАТЬ, а не повторять.
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
                    'posts': [],           # все посты с датами
                    'predictions': [],      # прогнозы
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
        """Создает смысловой хеш текста"""
        words = text.lower().split()
        important = [w for w in words if len(w) > 4 and w not in 
                    ['после', 'перед', 'через', 'около', 'только', 'также']]
        key_words = ' '.join(sorted(set(important))[:5])
        return hashlib.md5(key_words.encode()).hexdigest()[:8]
    
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
        """Генерирует пост с учетом памяти"""
        
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
            
            # Сохраняем пост
            self.brain['posts'].append({
                'date': self.today,
                'topic': topic,
                'title': main_title[:100],
                'post': post[:200],
                'semantic_hash': self.get_semantic_hash(post),
                'sources': sources_count
            })
            
            # Обновляем статистику
            if self.today not in self.brain['stats']['posts_by_date']:
                self.brain['stats']['posts_by_date'][self.today] = 0
            self.brain['stats']['posts_by_date'][self.today] += 1
            self.brain['stats']['total_posts'] += 1
            
            # Чистим старые посты
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