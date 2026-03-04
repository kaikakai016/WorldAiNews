import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
async def publish_to_channel(message: str, image_url: str = None):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        if image_url:
            try:
                await bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=image_url, caption=message[:1024], parse_mode='HTML')
                print("Published with image!")
                return True
            except TelegramError as e:
                print("Photo failed: " + str(e))
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message, parse_mode='HTML', disable_web_page_preview=False)
        print("Published!")
        return True
    except TelegramError as e:
        print("Telegram error: " + str(e))
        return False
async def publish_daily_summary(summary: str):
    await publish_to_channel("🌍 <b>СВОДКА</b>\n\n" + summary)
def run_publish(message: str):
    asyncio.run(publish_to_channel(message))