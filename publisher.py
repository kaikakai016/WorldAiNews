import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

async def publish_to_channel(message: str):
    """Публикует пост, разбивая на части если нужно"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Максимальная длина одного сообщения в Telegram
        MAX_LENGTH = 4000  # чуть меньше 4096 для запаса
        
        # Если пост короткий - отправляем целиком
        if len(message) <= MAX_LENGTH:
            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode='HTML'
            )
            print(f"✅ Пост опубликован ({len(message)} символов)")
            return True
        
        # Если длинный - разбиваем на части
        print(f"📎 Пост длинный ({len(message)} символов), разбиваю на части...")
        
        parts = []
        current_part = ""
        
        # Разбиваем по абзацам (не режем предложения)
        paragraphs = message.split('\n\n')
        
        for para in paragraphs:
            if len(current_part) + len(para) + 2 <= MAX_LENGTH:
                if current_part:
                    current_part += '\n\n' + para
                else:
                    current_part = para
            else:
                if current_part:
                    parts.append(current_part)
                current_part = para
        
        if current_part:
            parts.append(current_part)
        
        # Отправляем части по порядку
        for i, part in enumerate(parts):
            # Добавляем пометку о продолжении
            if len(parts) > 1:
                if i == 0:
                    part += "\n\n⬇️ ПРОДОЛЖЕНИЕ В СЛЕДУЮЩЕМ СООБЩЕНИИ"
                elif i == len(parts) - 1:
                    part = "⬆️ ПРОДОЛЖЕНИЕ\n\n" + part
                else:
                    part = "⬆️ ПРОДОЛЖЕНИЕ\n\n" + part + "\n\n⬇️ ПРОДОЛЖЕНИЕ СЛЕДУЕТ"
            
            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=part,
                parse_mode='HTML'
            )
            
            # Пауза между частями, чтобы не заспамить
            if i < len(parts) - 1:
                await asyncio.sleep(1)
        
        print(f"✅ Пост опубликован в {len(parts)} частях")
        return True
        
    except TelegramError as e:
        print(f"❌ Ошибка Telegram: {e}")
        return False