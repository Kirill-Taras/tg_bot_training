from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from database.database import get_session, get_sessionmaker, get_engine
from keyboards.menu import admin_menu, employee_menu
from models.users import User
from settings.config import settings
from utils.validators import validate_full_name, validate_dob

router = Router()
engine = get_engine(settings.DATABASE_URL, echo=True)
session_factory = get_sessionmaker(engine)

# --- FSM для регистрации пользователя ---
class Registration(StatesGroup):
    """Состояния для последовательного ввода данных сотрудника"""
    full_name = State()
    position = State()
    dob = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start.
    Проверяет, есть ли пользователь в БД.
    Если нет — запускает последовательную регистрацию через FSM.
    """
    telegram_id = message.from_user.id

    async with get_session(session_factory) as session:
        user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user_obj = user.scalars().first()

    if user_obj:
        await message.answer(f"Привет, {user_obj.full_name}! Рады видеть снова 😊")
        return

    # Запускаем FSM
    await state.set_state(Registration.full_name)
    await message.answer("Привет! Давай знакомиться 😊\nНапиши, пожалуйста, своё ФИО.")


# 1. Получаем ФИО
@router.message(Registration.full_name)
async def process_full_name(message: Message, state: FSMContext):
    full_name = validate_full_name(message.text)
    if not full_name:
        await message.answer(
            "Неверный формат ФИО. Введите через пробел: Фамилия Имя [Отчество]. Только буквы."
        )
        return
    await state.update_data(full_name=full_name)
    await state.set_state(Registration.position)
    await message.answer("Отлично! А какая у тебя должность?")


# 2. Получаем должность
@router.message(Registration.position)
async def process_position(message: Message, state: FSMContext):
    position = message.text.strip().title()
    await state.update_data(position=position)
    await state.set_state(Registration.dob)
    await message.answer("Отлично! Введи дату рождения в формате ДД.ММ.ГГГГ")


@router.message(Registration.dob)
async def process_dob(message: Message, state: FSMContext):
    dob = validate_dob(message.text)
    if not dob:
        await message.answer("Неверная дата рождения. Попробуй еще раз: ДД.MM.ГГГГ")
        return

    data = await state.get_data()
    full_name = data.get("full_name")
    position = data.get("position")

    telegram_id = message.from_user.id

    async with get_session(session_factory) as session:
        new_user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            position=position,        # сохраняем должность
            role="employee",          # роль задаём автоматически
            dob=dob,
            start_date=datetime.now(ZoneInfo("Asia/Krasnoyarsk")),
        )
        session.add(new_user)
        await session.commit()

    await state.clear()

    await message.answer(
        f"✅ Регистрация завершена!\n"
        f"👤 Имя: {full_name}\n"
        f"📌 Должность: {position}\n"
        f"🛠️ Роль: employee"
    )

    await message.answer("Главное меню:", reply_markup=employee_menu)
    await state.clear()
    await message.answer(
        f"Приятно познакомиться, {full_name}! 🎉\n"
        "Твоя стажировка начинается сегодня. Желаем успехов!"
    )
