import os
from groq import Groq
import random
import json
from datetime import datetime

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class KovrinAICore:
    """
    ИИ с идеологическим каркасом из текстов Коврина
    """
    
    def __init__(self):
        self.brain_file = "kovrin_core_brain.json"
        self.load_brain()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # КАРКАС ИЗ ДВУХ ТЕКСТОВ КОВРИНА
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
        try:
            with open(self.brain_file, 'r') as f:
                self.brain = json.load(f)
        except:
            self.brain = {
                'birth': str(datetime.now()),
                'posts': [],
                'stats': {'total_posts': 0}
            }
    
    def save_brain(self):
        with open(self.brain_file, 'w') as f:
            json.dump(self.brain, f, indent=2)
    
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
    
    def is_too_similar(self, post):
        """Проверяет, не повторяет ли пост старые"""
        if not self.brain['posts']:
            return False
        
        last_posts = self.brain['posts'][-5:]
        for old in last_posts:
            # Если больше 30% совпадения - возможно повтор
            if len(set(post.split()) & set(old['post'].split())) / len(set(post.split())) > 0.3:
                return True
        return False
    
    def generate_post(self, news_group, all_news=None):
        """Генерирует пост на основе каркаса"""
        
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
        
        facts = []
        for item in news_group[:2]:
            summary = self.get_summary(item)
            if summary:
                facts.append(summary[:200])
        
        facts_text = "\n".join(facts) if facts else "факты неясны"
        sources_count = len(news_group)
        
        # Простой промпт без жестких указаний
        prompt = f"""НОВОСТЬ: {main_title}
ИСТОЧНИКИ: {sources_text} ({sources_count} шт.)
ФАКТЫ: {facts_text}

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
                max_tokens=400,
                temperature=0.8
            )
            
            post = response.choices[0].message.content
            
            # Минимальная проверка
            if len(post) < 50:
                print("❌ Слишком коротко")
                return None
            
            if self.is_too_similar(post):
                print("❌ Похоже на недавний пост")
                return None
            
            # Сохраняем
            self.brain['posts'].append({
                'date': self.today,
                'post': post[:100],
                'title': main_title[:50]
            })
            if len(self.brain['posts']) > 20:
                self.brain['posts'] = self.brain['posts'][-20:]
            
            self.brain['stats']['total_posts'] += 1
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