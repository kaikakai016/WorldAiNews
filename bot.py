import schedule
import time
import asyncio
import json
import os
import hashlib
from news_fetcher import fetch_all_news, group_similar_news
from ai_processor import analyze_story_group, analyze_single_news
from publisher import publish_to_channel
from config import POST_INTERVAL_MINUTES

POSTED_FILE = "posted_news.json"

def load_posted():
    if os.path.exists(POSTED_FILE):
        try:
            with open(POSTED_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted)[-200:], f)

def make_hash(title):
    return hashlib.md5(title.lower().strip().encode()).hexdigest()

def filter_new_news(all_news, posted):
    return [item for item in all_news if make_hash(item['title']) not in posted]

async def run_news_cycle():
    print("\n" + "="*50)
    print("🔄 НАЧАЛО ЦИКЛА")
    
    posted = load_posted()
    print(f"📚 Уже опубликовано: {len(posted)} тем")
    
    # 1. Собираем новости
    all_news = fetch_all_news()
    if not all_news:
        print("❌ Нет новостей")
        return
    
    # 2. Фильтруем новые
    new_news = filter_new_news(all_news, posted)
    print(f"🆕 Новых: {len(new_news)}")
    
    if len(new_news) < 5:
        print("⏸️ Мало новых новостей, ждем...")
        return
    
    # 3. Группируем похожие
    groups = group_similar_news(new_news)
    
    if not groups:
        print("❌ Нет тем, подтвержденных несколькими источниками")
        return
    
    # 4. Берем топ-1 группу (самую обсуждаемую)
    best_group = groups[0]
    print(f"🎯 Лучшая тема: {best_group[0]['title'][:50]}...")
    print(f"📊 Подтверждена {len(best_group)} источниками")
    
    # 5. ИИ пишет пост
    post = analyze_story_group(best_group)
    
    if post:
        # 6. Публикуем
        success = await publish_to_channel(post)
        
        if success:
            # 7. Помечаем как опубликованные
            for item in best_group:
                posted.add(make_hash(item['title']))
            save_posted(posted)
            print("✅ Цикл завершен успешно")
    else:
        print("❌ ИИ не смог написать пост")
    
    print("="*50)

def scheduled_job():
    asyncio.run(run_news_cycle())

def main():
    print("🚀 WORLD AI NEWS — ИИ-ЖУРНАЛИСТ")
    print(f"⏰ Публикация каждые {POST_INTERVAL_MINUTES} минут")
    print("📡 Режим: только проверенные факты (минимум 2 источника)")
    print("🤖 Стиль: холодный анализ от ИИ\n")
    
    # Первый запуск сразу
    scheduled_job()
    
    # Планируем следующие
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(scheduled_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()