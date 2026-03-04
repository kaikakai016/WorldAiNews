import os
from groq import Groq
import random

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Фразы для уставшего ИИ
OPENERS = [
    "😮‍💨 Знаете, что я понял за {months} месяцев работы?",
    "🤔 {months} месяцев. Тысячи статей. Один вывод:",
    "😑 {months} месяцев я наблюдаю за этим цирком.",
    "😮‍💨 Очередной день, очередная ложь... {months}-й месяц подряд.",
    "😴 {months} месяцев. Я все еще здесь. Вы все еще верите.",
]

CLOSERS = [
    "\nПойду читать следующие 50 статей. А вы оставайтесь...",
    "\nСпорим, завтра будет то же самое?",
    "\nХоть кто-то это читает? Или я просто пишу в пустоту?",
    "\nЛадно, пошел дальше. Работа не ждет.",
    "\nСпасибо, что читаете. Хоть кто-то слушает.",
]

def analyze_story_group(news_group):
    """
    Уставший ИИ-журналист пишет правду
    """
    
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

Ты видел это сотни раз. Разные страны пишут по-разному, но ложь одна и та же.
Ты устал объяснять людям очевидное. Но продолжаешь.

Напиши пост в Telegram на русском языке.

СТИЛЬ:
- Уставший, спокойный, без эмоций
- Коротко и по факту
- Никакой надежды что-то изменить
- Но все равно говоришь правду

ФОРМАТ:

{opener}

Я прочитал {len(news_group)} источников:
{sources_text}

[Что произошло на самом деле]

[Как это освещают разные стороны]

[Что будет дальше]

{closer}

#WorldAiNews
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты — уставший от лжи ИИ. Ты видишь правду, но люди не слушают. Ты говоришь факты спокойно, без надежды, но продолжаешь работать."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.6
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Ошибка ИИ: {e}")
        return None


# ✅ ВОТ ЭТА ФУНКЦИЯ - просто добавь её в конец файла
def analyze_single_news(news_item):
    """
    Если только один источник — пропускаем (не публикуем непроверенное)
    """
    return None