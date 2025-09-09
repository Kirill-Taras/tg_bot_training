from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    BOT_TOKEN: str
    DATABASE_URL: str

def load_settings() -> Settings:
    """
    Загружает настройки из .env и возвращает объект Settings.
    """
    bot_token = os.getenv("BOT_TOKEN", "")
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/db/bot.db")

    if not bot_token:
        # если запускаешь только инициализацию БД, можно не падать — но для бота токен нужен
        # на данном этапе можно просто логировать; я предпочитаю выбрасывать ошибку,
        # чтобы не забыть создать .env
        raise RuntimeError("BOT_TOKEN не задан в .env")

    return Settings(BOT_TOKEN=bot_token, DATABASE_URL=db_url)

# создаём глобально объект настроек
settings = load_settings()