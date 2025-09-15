import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from handlers import start
from settings.config import settings
from services.scheduler import start_scheduler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env")

bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# подключаем маршрутизатор
dp.include_router(start.router)

# запуск бота
async def main():
    print("🚀 Бот запускается...")
    # подключаем рассылку
    start_scheduler(bot)
    try:
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("🛑 Бот остановлен пользователем")

if __name__ == "__main__":
    asyncio.run(main())
