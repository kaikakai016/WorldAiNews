import os
from dotenv import load_dotenv

load_dotenv()

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# AI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# News API
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Posting interval in minutes
try:
    POST_INTERVAL_MINUTES = int(os.getenv("POST_INTERVAL_MINUTES", 30))
except ValueError:
    raise ValueError("POST_INTERVAL_MINUTES must be a valid integer")

# RSS feeds from diverse global sources
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",         # BBC (UK)
    "https://rss.cnn.com/rss/edition_world.rss",            # CNN (USA)
    "https://www.aljazeera.com/xml/rss/all.xml",            # Al Jazeera (Qatar)
    "https://feeds.reuters.com/reuters/worldNews",           # Reuters (International)
    "https://rss.dw.com/rdf/rss-en-world",                  # DW (Germany)
    "https://www.france24.com/en/rss",                       # France24 (France)
    "https://feeds.skynews.com/feeds/rss/world.xml",        # Sky News (UK)
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
