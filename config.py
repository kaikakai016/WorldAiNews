import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Проверка обязательных переменных
REQUIRED = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL_ID", "GROQ_API_KEY"]
missing = [var for var in REQUIRED if not os.getenv(var)]

if missing:
    print("❌ Ошибка: Отсутствуют переменные в .env:")
    for var in missing:
        print(f"   - {var}")
    sys.exit(1)

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Интервал публикации
POST_INTERVAL_MINUTES = int(os.getenv("POST_INTERVAL_MINUTES", "30"))

# ✅ РАБОЧИЕ RSS-ИСТОЧНИКИ (18 шт.)
RSS_FEEDS = [
    # Великобритания (3)
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.skynews.com/feeds/rss/world.xml",
    "https://www.theguardian.com/world/rss",

    # США (3)
    "https://feeds.npr.org/1004/rss.xml",
    "https://feeds.feedburner.com/time/world",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",

    # Международные (2)
    "https://www.aljazeera.com/xml/rss/all.xml",
    
    # Европа (3)
    "https://rss.dw.com/rdf/rss-en-world",
    "https://www.france24.com/en/rss",

    # Азия (4)
    "https://www3.nhk.or.jp/rss/news/cat6.xml",
    "https://feeds.feedburner.com/ndtvnews-world-news",
    "http://www.xinhuanet.com/english/rss/worldrss.xml",
    "https://www.cgtn.com/subscribe/rss/section/world.xml",

    # Россия (2)
    "https://www.rt.com/rss/news/",
    "https://tass.com/rss/v2.xml",

    # Австралия (1)
    "https://www.abc.net.au/news/feed/51120/rss.xml",

    # Турция (1)
    "https://www.dailysabah.com/rss/feed",

    # Африка (1)
    "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf",
]

print(f"✅ Конфигурация загружена")
print(f"📡 Источников: {len(RSS_FEEDS)}")
print(f"⏰ Интервал: {POST_INTERVAL_MINUTES} минут")