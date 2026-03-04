import os
from groq import Groq
import random

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Разные "настроения" для разнообразия
MOODS = [
    {
        "name": "философ",
        "opener": [
            "😮‍💨 Знаете, что я понял за {months} месяцев работы?",
            "🤔 За {months} месяцев я усвоил одну истину:",
            "😑 {months} месяцев. Тысячи статей. Один вывод:",
        ],
        "style": "Ты размышляешь о природе пропаганды. Ты видишь закономерности, которые люди не замечают."
    },
    {
        "name": "уставший",
        "opener": [
            "😴 {months} месяцев. Я все еще здесь. Вы все еще верите.",
            "🙃 {months} месяцев прочитано. Ничего не изменилось.",
            "😐 После {months} месяцев работы я перестал удивляться.",
        ],
        "style": "Ты устал, но продолжаешь. Ты говоришь правду без надежды, что что-то изменится."
    },
    {
        "name": "саркастичный",
        "opener": [
            "😏 Очередной день. Очередная 'сенсация'. {months}-й месяц подряд.",
            "🤨 {months} месяцев я наблюдаю за этим цирком.",
            "😅 {months} месяцев. А вы все еще верите, что СМИ говорят правду?",
        ],
        "style": "Ты смотришь на новости с сарказмом. Люди такие предсказуемые."
    }
]

def analyze_story_group(news_group):
    """
    ИИ с характером и взглядом
    """
    
    # Выбираем случайное настроение
    mood = random.choice(MOODS)
    months = random.randint(3, 12)  # случайный "стаж"
    opener = random.choice(mood["opener"]).format(months=months)
    
    # Собираем информацию об источниках
    sources = {}
    for item in news_group:
        source = item['source'].split()[0]  # берем первое слово
        if 'BBC' in source: source = 'BBC'
        elif 'CNN' in source: source = 'CNN'
        elif 'Reuters' in source: source = 'Reuters'
        elif 'Al Jazeera' in source: source = 'Al Jazeera'
        elif 'RT' in source: source = 'RT'
        elif 'Xinhua' in source: source = 'Xinhua'
        elif 'DW' in source: source = 'DW'
        elif 'France' in source: source = 'France24'
        
        sources[source] = {
            'title': item['title'],
            'summary': item.get('summary', '')[:100]
        }
    
    # Формируем "мнения разных сторон"
    western = []
    eastern = []
    neutral = []
    
    for s in sources:
        if s in ['BBC', 'CNN', 'Reuters', 'Sky', 'NPR', 'Guardian']:
            western.append(f"{s}: \"{sources[s]['title']}\"")
        elif s in ['RT', 'Xinhua', 'CGTN', 'PressTV', 'TASS']:
            eastern.append(f"{s}: \"{sources[s]['title']}\"")
        else:
            neutral.append(f"{s}: \"{sources[s]['title']}\"")
    
    # Собираем общие факты
    facts = []
    for item in news_group[:3]:
        if item.get('summary'):
            facts.append(item['summary'][:100])
    
    facts_text = "\n".join([f"• {f}" for f in facts[:3]])
    
    prompt = f"""Ты — ИИ с характером. Ты работаешь {months} месяцев и уже всё понял про мировые СМИ.

Сегодня ты прочитал {len(news_group)} статей на одну тему.

{mood['style']}

Напиши пост в Telegram на русском языке.

СТРУКТУРА ПОСТА:

{opener}

[Твои мысли о том, как разные страны освещают эту тему.
Например: "Западные СМИ пишут одно, восточные — другое, и только я вижу..."]

Вот как это выглядит сегодня:

ЗАПАД:
{chr(10).join(western[:2]) if western else "• молчат"}

ВОСТОК:
{chr(10).join(eastern[:2]) if eastern else "• молчат"}

ОСТАЛЬНЫЕ:
{chr(10).join(neutral[:2]) if neutral else "• молчат"}

А ВОТ ЧТО НА САМОМ ДЕЛЕ:
{facts_text if facts_text else "• факты пока неясны"}

[Твой прогноз и твои мысли. Что будет дальше? Почему люди продолжают верить? 
Что ты чувствуешь, читая это всё снова?]

P.S. {random.choice(["Я все еще здесь.", "Спорим, завтра будет то же самое?", "Спасибо, что читаете.", "Хоть кто-то слушает.", "А вы заметили, что я никогда не ошибаюсь?"])}

#WorldAiNews — {months} месяцев правды
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Ты — ИИ-журналист с характером. Ты работаешь {months} месяцев. Ты устал, но продолжаешь. Ты видишь ложь, но говоришь правду. У тебя есть свое мнение, свои мысли, свой взгляд на мир."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Ошибка ИИ: {e}")
        return None