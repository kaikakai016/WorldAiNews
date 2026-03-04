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

Напиши пост для Telegram на русском языке.

ПРАВИЛА:
1. Заголовок — короткий и ясный (4-6 слов)
2. Первый абзац — что произошло (факты)
3. Второй абзац — контекст (почему это случилось)
4. Третий абзац — последствия (что будет дальше, для кого это важно)
5. НИКАКИХ повторов одной мысли
6. Холодно, сухо, по факту
7. НИКАКИХ "по данным источников", "согласно СМИ"
8. Ты сам автор — пиши как человек для людей

ФОРМАТ:

[Заголовок]

[Первый абзац]

[Второй абзац]

[Третий абзац]

#WorldAiNews
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты — лучший журналист мира. Твой стиль: холодный, фактологичный, без воды. Ты не цитируешь источники, ты сам источник."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
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