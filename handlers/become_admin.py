from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select

from database.database import get_engine, get_session, get_sessionmaker
from keyboards.menu import admin_menu  # добавим позже
from models.users import User
from settings.config import settings

router = Router()
engine = get_engine(settings.DATABASE_URL, echo=True)
session_factory = get_sessionmaker(engine)


class BecomeAdmin(StatesGroup):
    """FSM для ввода пароля администратора"""

    waiting_for_password = State()


@router.message(Command("become_admin"))
async def cmd_become_admin(message: Message, state: FSMContext):
    """Обрабатывает команду /become_admin — запрос пароля"""
    telegram_id = message.from_user.id

    async with get_session(session_factory) as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()

        if not user:
            await message.answer("⚠️ Сначала зарегистрируйся с помощью /start.")
            return

        if user.role == "admin":
            await message.answer("✅ Ты уже являешься администратором!")
            return

    await state.set_state(BecomeAdmin.waiting_for_password)
    await message.answer("🔐 Введи пароль администратора:")


@router.message(BecomeAdmin.waiting_for_password)
async def process_admin_password(message: Message, state: FSMContext):
    """Проверяет введённый пароль и обновляет роль пользователя"""
    password = message.text.strip()
    telegram_id = message.from_user.id

    if password != settings.ADMIN_ACCESS_CODE:
        await message.answer("❌ Неверный пароль. Доступ запрещён.")
        await state.clear()
        return

    async with get_session(session_factory) as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalars().first()

        if not user:
            await message.answer("⚠️ Сначала зарегистрируйся с помощью /start.")
            await state.clear()
            return

        user.role = "admin"
        await session.commit()

    await message.answer(
        "✅ Поздравляем! Теперь ты администратор 🧀", reply_markup=admin_menu
    )
    await state.clear()
