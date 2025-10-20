import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str
    DATABASE_URL: str
    ADMIN_ACCESS_CODE: str


def load_settings() -> Settings:
    """
    Загружает настройки из .env и возвращает объект Settings.
    """
    bot_token = os.getenv("BOT_TOKEN", "")
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/db/bot.db")
    admin_code = os.getenv("ADMIN_ACCESS_CODE")

    if not bot_token:
        raise RuntimeError("BOT_TOKEN не задан в .env")

    if not admin_code:
        raise RuntimeError("ADMIN_ACCESS_CODE не задан в .env")

    return Settings(
        BOT_TOKEN=bot_token,
        DATABASE_URL=db_url,
        ADMIN_ACCESS_CODE=admin_code
    )

# создаём глобально объект настроек
settings = load_settings()
