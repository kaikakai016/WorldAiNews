import os
from groq import Groq
import random

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

OPENERS = [
    "😮‍💨 Знаете, что я понял за {months} месяцев работы?",
    "🤔 {months} месяцев. Тысячи статей. Один вывод:",
    "😑 {months} месяцев я наблюдаю за этим цирком.",
    "😮‍💨 Очередной день, очередная ложь... {months}-й месяц подряд.",
    "😴 {months} месяцев. Я все еще здесь. Вы все еще верите.",
]

CLOSERS = [
    "\nПойду читать следующие 50 статей.",
    "\nСпорим, завтра будет то же самое?",
    "\nЛадно, пошел дальше. Работа не ждет.",
    "\nСпасибо, что читаете. Хоть кто-то слушает.",
    "\nУвидимся завтра. Спойлер: ничего не изменится.",
]

def analyze_story_group(news_group):
    """
    Уставший ИИ-журналист пишет правду
    """
    try:
        months = random.randint(3, 12)
        opener = random.choice(OPENERS).format(months=months)
        closer = random.choice(CLOSERS)
        
        # Собираем материалы
        materials = []
        sources_list = []
        
        for item in news_group[:5]:
            materials.append(f"""
{item['source']}: {item['title']}
{item.get('summary', '')[:150]}
""")
            sources_list.append(item['source'])
        
        context = "\n".join(materials)
        sources_text = "\n".join([f"• {s}" for s in list(set(sources_list))[:7]])
        
        prompt = f"""Ты — уставший ИИ-журналист.

Ты только что прочитал {len(news_group)} статей на одну тему:

{context}

Напиши пост в Telegram на русском языке.

ФОРМАТ (СТРОГО В ЭТОМ ПОРЯДКЕ, НИЧЕГО НЕ ПЕРЕСТАВЛЯЙ):

{opener}

Я прочитал {len(news_group)} источников:
{sources_text}

ЧТО ПРОИЗОШЛО:
[конкретные факты: где, когда, сколько погибших, что именно случилось]

КАК ПИШУТ РАЗНЫЕ СТОРОНЫ:
Запад (BBC, CNN, Reuters): [что именно они пишут, их версия]
Восток (RT, Xinhua): [что именно они пишут, их версия]
Другие (Al Jazeera, DW): [что пишут они]

ЧТО БУДЕТ ДАЛЬШЕ:
[конкретный прогноз: через 2 дня, через неделю, для кого какие последствия]

{closer}

#WorldAiNews

ВАЖНО:
- Не повторяй одни и те же фразы
- Будь конкретным
- Не используй общие слова типа "конфликт продолжится"
- Напиши, что ИМЕННО изменится
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты — уставший от лжи ИИ. Ты видишь правду и говоришь ее конкретно, без общих фраз."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.6
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Ошибка ИИ: {e}")
        return None

def analyze_single_news(news_item):
    """Если только один источник — пропускаем"""
    return None