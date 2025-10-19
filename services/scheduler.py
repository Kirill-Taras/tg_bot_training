import asyncio
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from database.database import get_engine, get_session, get_sessionmaker
from models.users import User
from settings.config import settings

# Часовой пояс Красноярска
KR_TIMEZONE = ZoneInfo("Asia/Krasnoyarsk")

# Сообщения на утро (опционально — можно потом убрать)
MORNING_MESSAGES = [
    "Доброе утро! 🌞 Пусть сегодняшний день принесёт новые знания и радость!",
    "С новым днём! Вдохновение и лёгкости в работе! 💪",
    "Привет! Начни день с улыбки и отличного настроения 😊",
]

# Сообщения по дням стажировки
DAILY_MESSAGES = {
    1: (
        "👋 Приветствуем тебя в команде «Сыроварня»! "
        "Мы рады, что ты с нами — впереди много интересного 😊\n\n"
        "Сегодня познакомься с **историей компании и нашей командой**:\n"
        "👉 [Ссылка на материал](https://example.com/history_team)"
    ),
    2: (
        "🔥 Привет! Первый день ты прошёл на ура 👏 "
        "Продолжаем в том же темпе!\n\n"
        "Сегодня самое время изучить **основные правила и стандарты работы**:\n"
        "👉 [Ссылка на материал](https://example.com/rules)"
    ),
    3: (
        "🎯 Отлично справляешься! Третий день — пора вникнуть глубже 💪\n\n"
        "Ознакомься с **твоими обязанностями и меню ресторана**:\n"
        "👉 [Ссылка на материал](https://example.com/menu_duties)"
    ),
}

# Настройка базы данных
engine = get_engine(settings.DATABASE_URL)
session_factory = get_sessionmaker(engine)

# Инициализация планировщика
scheduler = AsyncIOScheduler(timezone=KR_TIMEZONE)


async def send_morning_message(bot):
    """Отправляет утреннее сообщение всем стажёрам."""
    async with get_session(session_factory) as session:
        result = await session.execute(select(User).where(User.role == "intern"))
        users = result.scalars().all()

        for user in users:
            msg = random.choice(MORNING_MESSAGES)
            await bot.send_message(user.telegram_id, msg)


async def send_daily_message(bot):
    """Отправляет дневное сообщение стажёрам в зависимости от дня их стажировки."""
    async with get_session(session_factory) as session:
        result = await session.execute(select(User).where(User.role == "intern"))
        users = result.scalars().all()

        for user in users:
            if not user.start_date:
                continue

            delta_days = (
                datetime.now(KR_TIMEZONE).date() - user.start_date.date()
            ).days + 1
            message_text = DAILY_MESSAGES.get(delta_days)

            if message_text:
                await bot.send_message(
                    user.telegram_id, message_text, parse_mode="Markdown"
                )


def start_scheduler(bot):
    """Запускает планировщик с ежедневными задачами."""
    loop = asyncio.get_running_loop()

    # Утреннее сообщение в 10:00
    scheduler.add_job(
        lambda: loop.create_task(send_morning_message(bot)),
        CronTrigger(hour=10, minute=0),
    )
    # Основное сообщение в 10:05
    scheduler.add_job(
        lambda: loop.create_task(send_daily_message(bot)),
        CronTrigger(hour=10, minute=5),
    )

    scheduler.start()
    print("📅 Планировщик запущен (ежедневные сообщения активны)")
