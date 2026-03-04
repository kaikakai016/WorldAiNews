import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_story_group(news_group):
    """
    ИИ пишет свою версию событий на основе нескольких источников
    """
    
    # Собираем материалы для ИИ
    materials = []
    for item in news_group[:5]:  # берем топ-5 источников
        materials.append(f"""
ИСТОЧНИК: {item['source']}
ЗАГОЛОВОК: {item['title']}
СОДЕРЖАНИЕ: {item.get('summary', '')[:200]}
""")
    
    context = "\n---\n".join(materials)
    
    prompt = f"""Ты — независимый ИИ-журналист.

Ты прочитал {len(news_group)} статей на одну тему:

{context}

Теперь напиши СВОЮ версию событий. Не цитируй источники, не ставь ссылки. Просто расскажи, что произошло на самом деле.

Напиши пост для Telegram на русском языке по шаблону:

[КОРОТКИЙ ЗАГОЛОВОК, 4-6 слов]

[Первый абзац — суть события. Что произошло? Где? Когда?]

[Второй абзац — контекст. Почему это важно?]

[Третий абзац — твой анализ. Что будет дальше?]

#WorldAiNews

ВАЖНО:
- Ты — автор. Пиши как человек для людей.
- Никаких "по данным источников", "согласно СМИ"
- Только факты и холодный анализ
- Максимум 500 символов (это 3-4 предложения)
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты — лучший журналист мира. Твой стиль: холодный, фактологичный, без воды."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.5
        )
        
        post = response.choices[0].message.content
        
        # Добавляем эмодзи в начало если нужно
        if not post.startswith(('🌍', '💻', '💰', '🔬', '🌱')):
            post = "🌍 " + post
        
        return post
        
    except Exception as e:
        print(f"❌ Ошибка ИИ: {e}")
        return None

def analyze_single_news(news_item):
    """
    Если только один источник — пропускаем (не публикуем непроверенное)
    """
    return None  # Не публикуем одиночные новости