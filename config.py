import os
from dotenv import load_dotenv

load_dotenv()

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# AI settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# News API
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Posting interval in minutes
try:
    POST_INTERVAL_MINUTES = int(os.getenv("POST_INTERVAL_MINUTES", 30))
except ValueError:
    raise ValueError("POST_INTERVAL_MINUTES must be a valid integer")

# RSS feeds from diverse global sources
RSS_FEEDS = [
    # 🇬🇧 UK
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.skynews.com/feeds/rss/world.xml",
    "https://www.theguardian.com/world/rss",

    # 🇺🇸 USA
    "https://rss.cnn.com/rss/edition_world.rss",
    "https://feeds.npr.org/1004/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",

    # 🌍 International
    "https://feeds.reuters.com/reuters/worldNews",
    "https://www.aljazeera.com/xml/rss/all.xml",

    # 🇩🇪 Germany
    "https://rss.dw.com/rdf/rss-en-world",

    # 🇫🇷 France
    "https://www.france24.com/en/rss",

    # 🇯🇵 Japan
    "https://www3.nhk.or.jp/rss/news/cat6.xml",

    # 🇮🇳 India
    "https://feeds.feedburner.com/ndtvnews-world-news",

    # 🇦🇺 Australia
    "https://www.abc.net.au/news/feed/51120/rss.xml",

    # 🇨🇦 Canada
    "https://www.cbc.ca/cmlink/rss-world",

    # 🇰🇷 South Korea
    "https://koreajoongangdaily.joins.com/rss/feeds/worldnews.xml",

    # 🇨🇳 China
    "http://www.xinhuanet.com/english/rss/worldrss.xml",
    "https://www.cgtn.com/subscribe/rss/section/world.xml",
    "http://en.people.cn/rss/world.xml",

    # 🇷🇺 Russia (international perspective)
    "https://www.rt.com/rss/news/",

    # 🇧🇷 Brazil
    "https://www.bbc.com/portuguese/rss.xml",

    # 🇿🇦 Africa
    "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf",
]

# AI neutrality rules
NEUTRALITY_RULES = """
You are a neutral, independent news summarizer. Follow these strict rules:
1. Report ONLY verified facts (who, what, where, when)
2. NO opinions or editorial commentary
3. NO emotional language or charged words
4. NO political bias — treat all sides equally
5. Always cite the original source
6. If sources disagree, show BOTH perspectives
7. Use simple, clear English
8. Never use words like: good, bad, right, wrong, evil, hero, villain
9. Keep it factual and concise
"""