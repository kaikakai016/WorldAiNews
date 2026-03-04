import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

async def publish_to_channel(message: str):
    """Publish a message to the Telegram channel"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )
        print(f"✅ Published successfully!")
        return True
        
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")
        return False

async def publish_daily_summary(summary: str):
    """Publish a daily summary of top stories"""
    header = "🌍 <b>WORLD NEWS SUMMARY</b> 🌍\n\n"
    footer = "\n\n━━━━━━━━━━━━━━━\n🤖 <i>Powered by WorldAiNews — Independent AI News</i>"
    
    full_message = header + summary + footer
    await publish_to_channel(full_message)

def run_publish(message: str):
    """Synchronous wrapper for publishing"""
    asyncio.run(publish_to_channel(message))
