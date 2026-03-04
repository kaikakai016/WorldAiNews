import os
from groq import Groq
from config import NEUTRALITY_RULES

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CATEGORIES = {
    "🌍 Политика": ["politics", "government", "election", "president", "minister", "sanctions", "war", "peace", "nato", "treaty", "diplomat"],
    "💻 Технологии": ["tech", "ai", "artificial intelligence", "software", "hardware", "apple", "google", "microsoft", "openai", "robot", "cyber", "hack"],
    "💰 Экономика": ["economy", "market", "stock", "trade", "gdp", "inflation", "bank", "finance", "oil", "gas", "crypto", "bitcoin", "dollar"],
    "⚽ Спорт": ["sport", "football", "soccer", "basketball", "tennis", "olympic", "championship", "league", "match", "player", "team"],
    "🔬 Наука": ["science", "research", "study", "climate", "space", "nasa", "discovery", "health", "medical", "vaccine", "virus"],
    "⚡ Конфликты": ["war", "attack", "military", "army", "missile", "bomb", "conflict", "troops", "weapon", "killed", "strike"],
    "🌐 Общество": ["social", "culture", "education", "rights", "protest", "crime", "justice", "law", "court", "police"]
}

def detect_category(title, summary=""):
    text = (title + " " + summary).lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                return category
    return "🌐 Общество"

def get_hashtags(category):
    tags = {
        "🌍 Политика": "#Политика #МироваяПолитика",
        "💻 Технологии": "#Технологии #IT #ИИ",
        "💰 Экономика": "#Экономика #Финансы #Рынки",
        "⚽ Спорт": "#Спорт #МировойСпорт",
        "🔬 Наука": "#Наука #Здоровье #Исследования",
        "⚡ Конфликты": "#Конфликты #Безопасность",
        "🌐 Общество": "#Общество #МировыеНовости"
    }
    return tags.get(category, "#МировыеНовости")

def analyze_story_group(news_group):
    sources_lines = []
    for item in news_group:
        sources_lines.append(
            "Источник: " + item['source'] +
            "\nЗаголовок: " + item['title'] +
            "\nОписание: " + (item['summary'][:150] if item['summary'] else '') +
            "\nСсылка: " + item['link'] + "\n"
        )
    sources_text = "\n".join(sources_lines)
    source_names = " | ".join([item['source'] for item in news_group[:2]])
    count = len(news_group)

    category = detect_category(news_group[0]['title'], news_group[0].get('summary', ''))
    hashtags = get_hashtags(category)

    prompt = (
        "Ты — независимый ИИ-аналитик. Тебе дана одна новость от " + str(count) + " разных СМИ.\n\n"
        + sources_text + "\n\n"
        "Создай короткий пост для Telegram НА РУССКОМ ЯЗЫКЕ.\n"
        "ВАЖНО: весь пост НЕ БОЛЕЕ 900 символов!\n\n"
        "Формат (строго):\n"
        "🏷 " + category + "\n"
        "🌍 [тема — 1 строка]\n\n"
        "• [ключевой факт 1]\n"
        "• [ключевой факт 2]\n"
        "• [ключевой факт 3]\n\n"
        "🧠 [Независимый вывод ИИ — 1-2 предложения. Что это значит для мира?]\n\n"
        "🔗 " + source_names + "\n"
        + hashtags + " #МировыеНовости"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": NEUTRALITY_RULES}, {"role": "user", "content": prompt}],
            max_tokens=320,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI error: " + str(e))
        return None

def process_news_item(news_item):
    title = news_item['title']
    source = news_item['source']
    summary = news_item['summary']
    link = news_item['link']

    category = detect_category(title, summary)
    hashtags = get_hashtags(category)

    prompt = (
        "Ты — независимый ИИ-аналитик.\n"
        "Заголовок: " + title + "\n"
        "Источник: " + source + "\n"
        "Содержание: " + summary[:200] + "\n\n"
        "Создай короткий пост для Telegram НА РУССКОМ ЯЗЫКЕ.\n"
        "ВАЖНО: весь пост НЕ БОЛЕЕ 900 символов!\n\n"
        "Формат (строго):\n"
        "🏷 " + category + "\n"
        "📌 [заголовок — 1 строка]\n\n"
        "• [ключевой факт 1]\n"
        "• [ключевой факт 2]\n\n"
        "🧠 [Независимый вывод ИИ — 1-2 предложения. Что это значит?]\n\n"
        "🔗 " + source + "\n"
        + hashtags + " #МировыеНовости"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": NEUTRALITY_RULES}, {"role": "user", "content": prompt}],
            max_tokens=280,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI error: " + str(e))
        return None
