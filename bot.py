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

class URLGenerator:
    """Генератор URL в формате как в примере"""
    
    def __init__(self):
        # База доменов (как в ваших примерах)
        self.domains = [
            "i.oneme.ru",
            "l.oneme.ru", 
            "i.onieme.ru"
        ]
        
        # Типы изображений (tn параметр)
        self.image_types = [
            "sqr_96",
            "w_1440",
            "sqr_96", 
            "w_1440"
        ]
    
    def generate_random_string(self, length=60):
        """Генерирует случайную строку как в параметре r="""
        chars = string.ascii_letters + string.digits + '-_'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_hash_part(self, text=""):
        """Генерирует хеш часть как в ссылках"""
        # Берем текущее время + случайные символы
        base = f"{datetime.now().timestamp()}{random.randint(1000, 9999)}"
        return hashlib.md5(base.encode()).hexdigest()[:32]
    
    def generate_url(self, category="default", image_id=None):
        """
        Генерирует URL в формате:
        https://i.oneme.ru/i?tn=sqr_96&r=BTEFHNxXjmuR0N2Fir9SuMMR...
        """
        # Выбираем случайный домен
        domain = random.choice(self.domains)
        
        # Выбираем случайный тип изображения
        tn = random.choice(self.image_types)
        
        # Генерируем случайный параметр r
        # В примерах он очень длинный и похож на закодированные данные
        random_part = self.generate_random_string(70)
        hash_part = self.generate_hash_part()
        
        # Собираем r параметр как в примере
        r = f"BTEFHNxXjmuR0N2Fir9SuMMR{random_part}{hash_part}"
        
        # Обрезаем до длины как в примере (примерно 90-100 символов)
        r = r[:90]
        
        # Формируем полный URL
        url = f"https://{domain}/i?tn={tn}&r={r}"
        
        return url
    
    def generate_url_with_category(self, category):
        """
        Генерирует URL с учетом категории
        """
        domain = random.choice(self.domains)
        
        # Выбираем tn в зависимости от категории
        tn_map = {
            'tech': 'sqr_96',
            'nature': 'w_1440', 
            'people': 'sqr_96',
            'animals': 'w_1440',
            'default': random.choice(self.image_types)
        }
        
        tn = tn_map.get(category, tn_map['default'])
        
        # Генерируем r с включением категории
        base = f"{category}_{datetime.now().timestamp()}_{random.randint(1000, 9999)}"
        r_base = hashlib.md5(base.encode()).hexdigest()
        r = f"BTEF{r_base}{self.generate_random_string(50)}"
        r = r[:95]
        
        return f"https://{domain}/i?tn={tn}&r={r}"

# Создаем генератор
url_gen = URLGenerator()

async def post_generated_url():
    """
    Постит сгенерированный URL в канал
    """
    chat_id = Config.CHANNEL_ID
    
    # Генерируем URL
    url = url_gen.generate_url()
    
    # Категории для разнообразия
    categories = ['tech', 'nature', 'people', 'animals', 'default']
    category_url = url_gen.generate_url_with_category(random.choice(categories))
    
    # Выбираем случайно, какой URL постить
    if random.choice([True, False]):
        final_url = url
    else:
        final_url = category_url
    
    try:
        # Отправляем URL в канал
        await bot.send_message(
            chat_id=chat_id,
            text=final_url
        )
        print(f"✅ Опубликован URL: {final_url}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def scheduled_posting():
    """
    Постит URL по расписанию
    """
    await asyncio.sleep(10)
    
    while True:
        print(f"\n🔄 Генерация URL в {Config.get_current_time()}")
        
        success = await post_generated_url()
        
        if success:
            print(f"⏰ Следующий URL через {Config.POST_INTERVAL_HOURS} часа(ов)")
        else:
            print(f"⏰ Повтор через 5 минут")
            await asyncio.sleep(300)
            continue
        
        await asyncio.sleep(Config.POST_INTERVAL_HOURS * 60 * 60)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Я генерирую URL для картинок!")

@dp.message_handler(commands=['gen'])
async def manual_generate(message: types.Message):
    """Ручная генерация URL"""
    url = url_gen.generate_url()
    await message.reply(f"🎲 Сгенерированный URL:\n{url}")

if __name__ == '__main__':
    print("🚀 URL GENERATOR BOT STARTED")
    print(f"⏰ Интервал: {Config.POST_INTERVAL_HOURS} часа(ов)")
    print(f"📢 Канал: {Config.CHANNEL_ID}")
    print("="*40)
    
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled_posting())
    executor.start_polling(dp, skip_updates=True)