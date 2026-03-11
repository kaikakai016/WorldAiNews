# config.py
import os
from datetime import datetime, timedelta

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
    
    @staticmethod
    def get_current_time():
        return datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def get_next_post_time():
        """Время следующего поста (+5 минут)"""
        next_time = datetime.now() + timedelta(minutes=5)
        return next_time.strftime("%H:%M:%S")
    
    @staticmethod
    def validate():
        missing = []
        if not Config.TELEGRAM_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not Config.CHANNEL_ID:
            missing.append("TELEGRAM_CHANNEL_ID")
        
        if missing:
            print("❌ Ошибка: Отсутствуют переменные:")
            for var in missing:
                print(f"   - {var}")
            return False
        return True

if not Config.validate():
    print("⚠️ Бот не запустится без токена и ID канала")