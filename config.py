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

# 🌍 ПОЛНЫЙ СПИСОК ИСТОЧНИКОВ - 27 СМИ СО ВСЕГО МИРА
RSS_FEEDS = [
    # 🇬🇧 Великобритания (3)
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.skynews.com/feeds/rss/world.xml",
    "https://www.theguardian.com/world/rss",

    # 🇺🇸 США (4)
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://feeds.npr.org/1004/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.feedburner.com/time/world",

    # 🌍 Международные агентства (3)
    "https://feeds.reuters.com/reuters/worldNews",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://apnews.com/apf-worldnews",

    # 🇩🇪 Германия (1)
    "https://rss.dw.com/rdf/rss-en-world",

    # 🇫🇷 Франция (1)
    "https://www.france24.com/en/rss",

    # 🇯🇵 Япония (1)
    "https://www3.nhk.or.jp/rss/news/cat6.xml",

    # 🇮🇳 Индия (1)
    "https://feeds.feedburner.com/ndtvnews-world-news",

    # 🇦🇺 Австралия (1)
    "https://www.abc.net.au/news/feed/51120/rss.xml",

    # 🇨🇦 Канада (1)
    "https://www.cbc.ca/cmlink/rss-world",

    # 🇰🇷 Южная Корея (1)
    "https://koreajoongangdaily.joins.com/rss/feeds/worldnews.xml",

    # 🇨🇳 Китай (3)
    "http://www.xinhuanet.com/english/rss/worldrss.xml",
    "https://www.cgtn.com/subscribe/rss/section/world.xml",
    "http://en.people.cn/rss/world.xml",

    # 🇷🇺 Россия (2)
    "https://www.rt.com/rss/news/",
    "https://tass.com/rss/v2.xml",

    # 🇧🇷 Бразилия (1)
    "https://www.bbc.com/portuguese/rss.xml",

    # 🇿🇦 Африка (1)
    "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf",

    # 🇹🇷 Турция (1)
    "https://www.dailysabah.com/rss/feed",

    # 🇮🇱 Израиль (1)
    "https://www.haaretz.com/cmlink/1.1596990",

    # 🇮🇷 Иран (1)
    "https://www.presstv.ir/feeds/english",

    # 🇪🇬 Египет (1)
    "https://english.ahram.org.eg/News/rss/0.aspx",
]

# Правила для ИИ (коротко)
NEUTRALITY_RULES = "Ты независимый ИИ-журналист. Пиши факты холодно, без эмоций. Ты видишь все стороны."

print(f"✅ Конфигурация загружена")
print(f"📡 Источников: {len(RSS_FEEDS)}")
print(f"⏰ Интервал: {POST_INTERVAL_MINUTES} минут")