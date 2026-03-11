# config.py
import os
from datetime import datetime

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
    POST_INTERVAL_HOURS = int(os.getenv('POST_INTERVAL_HOURS', '3'))
    
    @staticmethod
    def get_current_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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