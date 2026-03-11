# bot.py
import asyncio
import random
from aiogram import Bot, Dispatcher, executor, types
from config import Config

# Инициализация бота
bot = Bot(token=Config.TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Список URL с картинками (ваши ссылки)
IMAGE_URLS = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
    "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800",
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800",
    "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800",
    "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800",
    "https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg?w=800",
    "https://images.pexels.com/photos/11064744/pexels-photo-11064744.jpeg?w=800",
    # Добавьте свои ссылки сюда
]

async def post_random_image():
    """
    Постит случайную картинку из списка
    """
    chat_id = Config.CHANNEL_ID
    
    # Выбираем случайную картинку
    image_url = random.choice(IMAGE_URLS)
    
    try:
        # Отправляем фото без подписи
        await bot.send_photo(
            chat_id=chat_id,
            photo=image_url,
            caption=""  # Пустая подпись
        )
        print(f"✅ Постнул картинку: {image_url[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def scheduled_posting():
    """
    Постит картинки по расписанию
    """
    # Ждем 10 секунд при запуске
    await asyncio.sleep(10)
    
    while True:
        print(f"\n🔄 Постинг в {Config.get_current_time()}")
        
        # Постим картинку
        success = await post_random_image()
        
        if success:
            print(f"⏰ Следующий пост через {Config.POST_INTERVAL_HOURS} часа(ов)")
        else:
            print(f"⏰ Повтор через 5 минут (после ошибки)")
            await asyncio.sleep(300)  # 5 минут
            continue
        
        # Ждем указанный интервал
        await asyncio.sleep(Config.POST_INTERVAL_HOURS * 60 * 60)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Ответ на команды start и help"""
    await message.reply("Я бот для постинга картинок в канал!")

@dp.message_handler(commands=['post'])
async def manual_post(message: types.Message):
    """Ручной постинг картинки"""
    if message.chat.id == int(Config.CHANNEL_ID) or str(message.chat.id) == Config.CHANNEL_ID:
        success = await post_random_image()
        if success:
            await message.reply("✅ Картинка опубликована")
        else:
            await message.reply("❌ Ошибка публикации")

if __name__ == '__main__':
    print("🚀 IMAGE BOT STARTED")
    print(f"⏰ Интервал: {Config.POST_INTERVAL_HOURS} часа(ов)")
    print(f"📸 Картинок в базе: {len(IMAGE_URLS)}")
    print(f"📢 Канал: {Config.CHANNEL_ID}")
    print("="*40)
    
    # Запускаем планировщик и бота
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled_posting())
    executor.start_polling(dp, skip_updates=True)