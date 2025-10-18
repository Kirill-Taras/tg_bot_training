import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.admin import add_material, delete_material, manage_users
from settings.config import settings
from database.database import get_engine, get_sessionmaker, init_db

from handlers import start, menu, contacts, educational_material, restaurant_menu
from services.scheduler import start_scheduler


async def main():
    print("🚀 Бот запускается...")

    # --- Настройка базы ---
    engine = get_engine(settings.DATABASE_URL, echo=True)
    session_factory = get_sessionmaker(engine)
    await init_db(engine)  # создаёт таблицы, если их нет

    # --- Настройка бота ---
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # --- Подключаем роутеры ---
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(contacts.router)
    dp.include_router(educational_material.router)
    dp.include_router(restaurant_menu.router)
    dp.include_router(add_material.router)
    dp.include_router(delete_material.router)
    dp.include_router(manage_users.router)

    # --- Запускаем планировщик рассылок ---
    start_scheduler(bot)

    # --- Запуск бота ---
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("🛑 Бот остановлен пользователем")


if __name__ == "__main__":
    asyncio.run(main())