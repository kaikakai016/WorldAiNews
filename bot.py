# bot.py
import asyncio
import random
import string
import hashlib
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from config import Config

# Инициализация бота
bot = Bot(token=Config.TELEGRAM_TOKEN)
dp = Dispatcher(bot)

class PhotoURLGenerator:
    """Генератор URL для фото как в примере"""
    
    def __init__(self):
        # Домены из ваших примеров
        self.domains = [
            "i.oneme.ru",
            "l.oneme.ru",
            "i.onieme.ru",
            "oneme.ru"
        ]
        
        # Типы изображений (tn параметры из примеров)
        self.image_types = [
            "sqr_96",
            "w_1440", 
            "5qr_96",
            "sqr_96",
            "w_1440"
        ]
        
        # База для генерации r параметра
        self.base_strings = [
            "BTEFHNxXjmuR0N2Fir9SuMMR",
            "BUFxtygYfQ8hpBNJRyp5v4T3",
            "BTEFHNxXjmuR0N2Flr9SuMMR",
            "BUFxtygY1Q8hpBNJ"
        ]
    
    def generate_random_string(self, length=50):
        """Генерирует случайную строку"""
        chars = string.ascii_letters + string.digits + '-_/'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_hash(self):
        """Генерирует хеш часть"""
        timestamp = str(datetime.now().timestamp()).replace('.', '')
        random_num = str(random.randint(1000, 9999))
        base = timestamp + random_num
        return hashlib.md5(base.encode()).hexdigest()[:20]
    
    def generate_one_url(self):
        """
        Генерирует ОДИН URL в формате из примера
        """
        # Выбираем случайные компоненты
        domain = random.choice(self.domains)
        tn = random.choice(self.image_types)
        base = random.choice(self.base_strings)
        
        # Генерируем остальные части
        part1 = self.generate_random_string(30)
        part2 = self.generate_hash()
        part3 = self.generate_random_string(15)
        
        # Собираем r параметр как в примерах
        # Получается примерно: BTEFHNxXjmuR0N2Fir9SuMMR... -O5qxacvtOZSHRk91-7yg
        r = f"{base}{part1}{part2}-O5q{part3}"
        
        # Обрезаем до нужной длины (как в примерах)
        r = r[:95]
        
        # Формируем полный URL
        url = f"https://{domain}/i?tn={tn}&r={r}"
        
        return url
    
    def generate_batch(self, count=10):
        """
        Генерирует пачку URL
        """
        urls = []
        for _ in range(count):
            url = self.generate_one_url()
            urls.append(url)
        return urls

# Создаем генератор
generator = PhotoURLGenerator()

async def post_photo_batch():
    """
    Постит 10 сгенерированных URL в канал
    """
    chat_id = Config.CHANNEL_ID
    
    try:
        # Генерируем 10 URL
        urls = generator.generate_batch(10)
        
        # Форматируем сообщение
        current_time = datetime.now().strftime("%H:%M:%S")
        message = f"🖼️ **ФОТО ({current_time})**\n\n"
        
        for i, url in enumerate(urls, 1):
            message += f"{i}. {url}\n\n"
        
        message += f"⏱️ Следующая партия через 5 минут"
        
        # Отправляем в Telegram
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
        
        print(f"✅ Опубликовано 10 URL в {current_time}")
        print(f"   Пример: {urls[0][:60]}...")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def scheduled_posting():
    """
    Постит каждые 5 минут
    """
    print("⏳ Запуск через 10 секунд...")
    await asyncio.sleep(10)
    
    post_count = 0
    
    while True:
        post_count += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{'='*50}")
        print(f"🔄 ПОСТ #{post_count} | {current_time}")
        
        # Постим 10 фото
        success = await post_photo_batch()
        
        if success:
            print(f"⏰ Следующий пост через 5 минут (в {Config.get_next_post_time()})")
        else:
            print(f"⏰ Ошибка, повтор через 1 минуту")
            await asyncio.sleep(60)
            continue
        
        # Ждем ровно 5 минут (300 секунд)
        await asyncio.sleep(300)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(
        "🖼️ **Photo URL Bot**\n\n"
        "Я генерирую URL для фото как в ваших примерах.\n"
        f"📢 Постинг каждые 5 минут по 10 фото в канал.\n\n"
        "Команды:\n"
        "/test - сгенерировать 1 тестовый URL\n"
        "/batch - сгенерировать 10 URL сейчас"
    )

@dp.message_handler(commands=['test'])
async def test_generate(message: types.Message):
    """Тестовая генерация одного URL"""
    url = generator.generate_one_url()
    await message.reply(f"🎲 **Тестовый URL:**\n`{url}`", parse_mode='Markdown')

@dp.message_handler(commands=['batch'])
async def manual_batch(message: types.Message):
    """Ручная генерация 10 URL"""
    urls = generator.generate_batch(10)
    response = "🎲 **Сгенерировано 10 URL:**\n\n"
    for i, url in enumerate(urls, 1):
        response += f"{i}. `{url}`\n\n"
    await message.reply(response, parse_mode='Markdown')

if __name__ == '__main__':
    print("="*50)
    print("🚀 PHOTO URL BOT — МОЩНЫЙ РЕЖИМ")
    print("="*50)
    print(f"📢 Канал: {Config.CHANNEL_ID}")
    print(f"⏰ Режим: КАЖДЫЕ 5 МИНУТ")
    print(f"🖼️ За раз: 10 ФОТО")
    print(f"📊 В час: 120 фото")
    print(f"📊 В день: ~2880 фото")
    print("="*50)
    
    # Запускаем
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled_posting())
    executor.start_polling(dp, skip_updates=True)