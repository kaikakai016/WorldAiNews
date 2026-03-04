# 🌍 WorldAiNews — Independent AI News Bot for Telegram

## What is this?
WorldAiNews is an autonomous AI-powered Telegram news bot that:
- Collects world news from 7+ international sources (BBC, CNN, Al Jazeera, Reuters, DW, France24, Sky News)
- Processes all news through AI to ensure neutrality
- Finds stories confirmed by multiple sources
- Publishes factual, unbiased summaries to your Telegram channel automatically

## 🛠️ Setup Guide (Step by Step)

### Step 1: Get your Telegram Bot Token
1. Open Telegram and search for @BotFather
2. Send `/newbot`
3. Follow instructions and copy your token

### Step 2: Get OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up / Login
3. Go to API Keys section
4. Create new key and copy it

### Step 3: Get NewsAPI Key (Free)
1. Go to [newsapi.org](https://newsapi.org)
2. Sign up for free
3. Copy your API key

### Step 4: Setup the bot
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. Fill in your keys in `.env`
5. Run: `python bot.py`

## 📋 How it works
```
Every 30 minutes:
1. Fetch news from 7 global sources
2. AI finds stories confirmed by multiple sources
3. AI summarizes each story neutrally
4. Posts to your Telegram channel
```

## ⚙️ Configuration
Edit `.env` file to customize:
- `POST_INTERVAL_MINUTES` — how often to post (default: 30)
- `TELEGRAM_CHANNEL_ID` — your channel username

## 🤖 AI Neutrality Rules
The AI follows strict rules:
- Only verified facts
- No opinions or bias
- Shows all perspectives
- Always cites sources

## 📦 Tech Stack
- Python 3.10+
- python-telegram-bot
- OpenAI GPT-4
- feedparser (RSS)
- NewsAPI
