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

# Интервал публикации (по умолчанию 30 минут)
POST_INTERVAL_MINUTES = int(os.getenv("POST_INTERVAL_MINUTES", "30"))

# RSS источники (топовые мировые СМИ)
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.dw.com/rdf/rss-en-world",
    "https://www.france24.com/en/rss",
    "https://feeds.skynews.com/feeds/rss/world.xml",
    "https://feeds.npr.org/1004/rss.xml",
]

# Правила для ИИ (коротко и ясно)
NEUTRALITY_RULES = "Ты независимый журналист. Пиши факты холодно и без эмоций."