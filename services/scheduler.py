import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo
import random
from sqlalchemy import select

from database.database import get_engine, get_sessionmaker, get_session
from models.users import User
from models.materials import Material
from settings.config import settings

# Временная зона Красноярск
KR_TIMEZONE = ZoneInfo("Asia/Krasnoyarsk")

# Списки утренних мотиваций/фактов
MORNING_MESSAGES = [
    "Доброе утро! 🌞 Сегодня отличный день для обучения!",
    "С новым днём! Вдохновение и успех ждут тебя!",
    "Привет! Начни день с улыбки и новых знаний!",
]

engine = get_engine(settings.DATABASE_URL)
session_factory = get_sessionmaker(engine)

scheduler = AsyncIOScheduler(timezone=KR_TIMEZONE)

async def send_morning_message(bot):
    """
    Отправка мотивационного сообщения каждому сотруднику.
    """
    async with get_session(session_factory) as session:
        result = await session.execute(
            select(User).where(User.status == "стажировка")  # только активные
        )
        users = result.scalars().all()

        for user in users:
            msg = random.choice(MORNING_MESSAGES)
            await bot.send_message(user.telegram_id, msg)


async def send_daily_material(bot):
    """
    Отправка учебного материала в зависимости от дня стажировки.
    """
    async with get_session(session_factory) as session:
        users_result = await session.execute(
            select(User).where(User.status == "стажировка")
        )
        users = users_result.scalars().all()

        for user in users:
            # считаем день стажировки
            delta_days = (datetime.now(KR_TIMEZONE).date() - user.start_date.date()).days + 1

            # ограничим 1–5 день
            if 1 <= delta_days <= 5:
                mat_result = await session.execute(
                    select(Material).where(Material.day == delta_days)
                )
                material = mat_result.scalars().first()
                if material:
                    text = material.text or ""
                    await bot.send_message(user.telegram_id, text)



def start_scheduler(bot):
    loop = asyncio.get_running_loop()

    # Утро — 8:00 Красноярск
    scheduler.add_job(
        lambda: loop.create_task(send_morning_message(bot)),
        CronTrigger(hour=16, minute=28)
    )

    # Днём — 12:00 Красноярск
    scheduler.add_job(
        lambda: loop.create_task(send_daily_material(bot)),
        CronTrigger(hour=22, minute=29)
    )

    scheduler.start()