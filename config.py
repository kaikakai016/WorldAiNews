# config.py
import os
from datetime import datetime

class Config:
    # Telegram (обязательные переменные)
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Токен бота
    CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')      # ID канала (@channel или -100123456789)
    
    # Настройки постинга
    POST_INTERVAL_HOURS = int(os.getenv('POST_INTERVAL_HOURS', '3'))  # Каждые 3 часа
    
    @staticmethod
    def get_current_time():
        """Возвращает текущее время в читаемом формате"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def validate():
        """Проверяет наличие обязательных переменных"""
        missing = []
        if not Config.TELEGRAM_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not Config.CHANNEL_ID:
            missing.append("TELEGRAM_CHANNEL_ID")
        
        if missing:
            print("❌ Ошибка: Отсутствуют переменные окружения:")
            for var in missing:
                print(f"   - {var}")
            return False
        return True

# Проверка при импорте
if not Config.validate():
    print("⚠️ Бот не сможет запуститься без токена и ID канала")