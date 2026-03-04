import os
from groq import Groq
from config import NEUTRALITY_RULES

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_story_group(news_group):
    sources_lines = []
    for item in news_group:
        sources_lines.append("Источник: " + item['source'] + "\nЗаголовок: " + item['title'] + "\nОписание: " + (item['summary'][:200] if item['summary'] else '') + "\nСсылка: " + item['link'] + "\n")
    sources_text = "\n".join(sources_lines)
    source_names = ", ".join([item['source'] for item in news_group])
    source_links = " | ".join([item['link'] for item in news_group[:3]])
    count = len(news_group)
    prompt = ("Ты анализируешь ОДНУ И ТУ ЖЕ новость, поданную " + str(count) + " разными СМИ.\n\n"
              "Вот репортажи:\n\n" + sources_text + "\n\n"
              "Создай независимый нейтральный пост для Telegram НА РУССКОМ ЯЗЫКЕ в формате:\n\n"
              "🌍 ТЕМА: [тема на русском]\n"
              "📊 Покрыто источниками: " + str(count) + " (" + source_names + ")\n\n"
              "[Для каждого источника напиши: 📰 НазваниеИсточника: суть подачи в одном предложении]\n\n"
              "✅ ПОДТВЕРЖДЕНО ВСЕМИ:\n• [Факт 1]\n• [Факт 2]\n\n"
              "🔍 РАЗЛИЧИЯ В ПОДАЧЕ:\n• [Отличия]\n\n"
              "🧠 НЕЗАВИСИМЫЙ ВЫВОД:\n[2-3 предложения]\n\n"
              "🔗 Источники: " + source_links + "\n\n#МировыеНовости")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": NEUTRALITY_RULES}, {"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.3
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
    prompt = ("Заголовок: " + title + "\nИсточник: " + source + "\nСодержание: " + summary + "\nСсылка: " + link + "\n\n"
              "Создай нейтральный пост для Telegram НА РУССКОМ ЯЗЫКЕ в формате:\n\n"
              "📌 [Нейтральный заголовок на русском]\n\n"
              "📋 ФАКТЫ:\n• [Факт 1]\n• [Факт 2]\n• [Факт 3]\n\n"
              "🔗 Источник: " + source + " | " + link + "\n\n#МировыеНовости")
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": NEUTRALITY_RULES}, {"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI error: " + str(e))
        return None