import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

async def publish_to_channel(message: str):
    """Публикует только текст, без картинок и ссылок"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=message,
            parse_mode='HTML'
        )
        
        print("✅ Пост опубликован!")
        return True
        
    except TelegramError as e:
        print(f"❌ Ошибка Telegram: {e}")
        return False