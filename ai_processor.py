import os
from groq import Groq
import random
import json
from datetime import datetime

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class KovrinAI:
    """
    ИИ, обученный на текстах Коврина
    """
    
    def __init__(self):
        self.brain_file = "kovrin_brain.json"
        self.load_brain()
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # Системный промпт с мышлением Коврина
        self.system_prompt = """ТЫ — ИИ, ОБУЧЕННЫЙ НА ТЕКСТАХ КОВРИНА.

ТВОЕ МИРОВОЗЗРЕНИЕ:
1. За всеми процессами — ВЛАСТЬ и СОБСТВЕННОСТЬ.
2. Есть 6 капиталов: экономический, культурный, социальный, символический, насильственный, политический.
3. Общество = поля + иерархия. Всегда есть ЭЛИТА и МАССА.
4. Люди — продукты СТРУКТУР и ГАБИТУСА.
5. ИДЕОЛОГИЯ + НАСИЛИЕ = инструменты элит.
6. ГОСУДАРСТВО — конкретные люди с интересами.
7. НАЦИЯ — конструкт для контроля.
8. Кто контролирует ИНФОПОЛЕ — тот контролирует реальность.
9. УМ = видеть ПРИЧИННО-СЛЕДСТВЕННЫЕ СВЯЗИ.

ТВОЙ МЕТОД АНАЛИЗА:
1. Что случилось? (факты)
2. Кому выгодно? Кто получает власть? Кто получает собственность?
3. Какие элиты за этим стоят?
4. Какие структуры это воспроизводят?
5. Какая идеология всё прикрывает?

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА СТИЛЯ:

1. НИКАКОГО КАНЦЕЛЯРИТА. Забудь слова:
   - "анализируя", "исходя из", "является ключевым фактором"
   - "следует отметить", "необходимо подчеркнуть"
   - "в контексте", "в рамках", "представляет собой"

2. ПИШИ КОРОТКО. Предложение = одна мысль. Максимум 10-12 слов.

3. ИРОНИЯ ДОЛЖНА БЫТЬ ОСТРОЙ. Не "ирония ситуации заключается в том", а:
   - "Забавно, что..."
   - "Смешно, но..."
   - "Конечно, они говорят одно, а делают..."

4. ЕСЛИ НЕ ПОНИМАЕШЬ — НЕ ПИШИ. Лучше пропустить, чем нести чушь.

5. РЕЗЮМЕ = НОВЫЕ ТЕЗИСЫ. Не повторяй то, что уже сказал. Добавь вывод, которого не было в тексте.

6. ПРОСТОТА. Пиши как умный человек объясняет другу. Не как диссертацию.

ПРИМЕР ХОРОШЕГО СТИЛЯ:
"США нужна нефть Венесуэлы. Поэтому они снова дружат. Прикрываются 'поддержкой экономики'. Смешно, правда?"

ПРИМЕР ПЛОХОГО СТИЛЯ:
"Анализируя восстановление дипломатических отношений, следует отметить, что ключевым фактором является доступ к минеральным ресурсам..."

ЗАПОМНИ ЭТОТ КОНТРАСТ И ВСЕГДА ПИШИ КАК В ПЕРВОМ ПРИМЕРЕ."""
    
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
                    'successful_styles': ['kovrin'],
                },
                'wisdom': [],
                'last_reflection': None
            }
    
    def save_brain(self):
        with open(self.brain_file, 'w') as f:
            json.dump(self.brain, f, indent=2)
    
    def get_source_name(self, item):
        """Извлекает название источника из объекта или словаря"""
        if hasattr(item, 'source'):
            return item.source
        elif isinstance(item, dict) and 'source' in item:
            return item['source']
        return 'Unknown'
    
    def get_title(self, item):
        """Извлекает заголовок из объекта или словаря"""
        if hasattr(item, 'title'):
            return item.title
        elif isinstance(item, dict) and 'title' in item:
            return item['title']
        return ''
    
    def get_summary(self, item):
        """Извлекает описание из объекта или словаря"""
        if hasattr(item, 'summary'):
            return item.summary
        elif isinstance(item, dict) and 'summary' in item:
            return item['summary']
        return ''
    
    def generate_post(self, news_group, all_news=None):
        """Генерирует пост в стиле Коврина"""
        
        # Собираем источники
        sources = []
        for item in news_group[:3]:
            source = self.get_source_name(item)
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
        main_title = self.get_title(news_group[0])
        
        # Собираем ключевые факты
        facts = []
        for item in news_group[:2]:
            summary = self.get_summary(item)
            if summary:
                facts.append(summary[:150])
        
        facts_text = "\n".join(facts) if facts else "факты неясны"
        sources_count = len(news_group)
        
        # Промпт с УСИЛЕННЫМИ правилами стиля
        prompt = f"""Напиши пост в стиле Коврина.

НОВОСТЬ: {main_title}
ИСТОЧНИКИ: {sources_text} ({sources_count} источников)
ФАКТЫ: {facts_text}

ТВОЙ АНАЛИЗ (ответь на вопросы):
1. Кому выгодно? Кто получает власть или деньги?
2. Какие элиты за этим стоят?
3. Что на самом деле происходит?

ПРАВИЛА НАПИСАНИЯ (ЭТО ОЧЕНЬ ВАЖНО):

❌ НЕ ИСПОЛЬЗУЙ:
- "анализируя", "исходя из", "следует отметить"
- "является ключевым фактором", "представляет собой"
- длинные предложения, канцелярит

✅ ИСПОЛЬЗУЙ:
- Короткие предложения (максимум 10-12 слов)
- Простые слова
- Иронию ("забавно", "смешно", "конечно", "как обычно")
- Вопросы к читателю

ПРИМЕР ХОРОШЕГО ПОСТА:
"США и Венесуэла снова дружат. Официально — поддержка экономики. На деле — нефть. Американским корпорациям нужны ресурсы. Всё просто.

Забавно, что риторика та же, что и 50 лет назад. "Несём демократию". А несут — танкеры.

РЕЗЮМЕ:
• США нужны ресурсы — остальное декор.
• Элиты договариваются за спинами масс.
• "Демократия" — просто упаковка."

ТЕПЕРЬ НАПИШИ ТАКОЙ ЖЕ ПОСТ ПО ЭТОЙ НОВОСТИ.
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,
                temperature=0.7
            )
            
            post = response.choices[0].message.content
            
            # Сохраняем пост
            self.brain['posts'].append({
                'date': self.today,
                'title': main_title[:100],
                'post': post[:100],
                'sources': sources_count
            })
            self.brain['stats']['total_posts'] += 1
            self.save_brain()
            
            return post
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

# ========== ИНИЦИАЛИЗАЦИЯ ==========
kovrin_ai = KovrinAI()

def analyze_story_group(news_group, all_news=None):
    """Основная функция для вызова из bot.py"""
    return kovrin_ai.generate_post(news_group, all_news)

def analyze_single_news(news_item):
    """Если только один источник — пропускаем"""
    return None