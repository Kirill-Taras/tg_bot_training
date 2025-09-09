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
    role = State()
    dob = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start.
    Проверяет, есть ли пользователь в БД.
    Если нет — запускает последовательную регистрацию через FSM.
    """
    telegram_id = message.from_user.id
    session_factory = get_sessionmaker(engine)

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
    await state.set_state(Registration.role)
    await message.answer("Отлично! А какая у тебя должность?")


# 2. Получаем должность
@router.message(Registration.role)
async def process_role(message: Message, state: FSMContext):
    role = message.text.strip().title()
    await state.update_data(role=role)
    await state.set_state(Registration.dob)
    await message.answer("Отлично! Введи дату рождения в формате ДД.ММ.ГГГГ")


# 3. Получаем дату рождения и сохраняем данные
@router.message(Registration.dob)
async def process_dob(message: Message, state: FSMContext):
    session_factory = get_sessionmaker(engine)
    dob = validate_dob(message.text)
    if not dob:
        await message.answer(
            "Неверная дата рождения. Попробуй еще раз: ДД.MM.ГГГГ или '12 марта 2000'."
        )
        return
    data = await state.get_data()
    full_name = data.get("full_name")
    role = data.get("role")

    telegram_id = message.from_user.id

    # Сохраняем в БД
    async with get_session(session_factory) as session:
        new_user = User(
            telegram_id=telegram_id,
            full_name=full_name,
            role=role,
            dob=dob,
            start_date=datetime.now(ZoneInfo("Asia/Krasnoyarsk"))
        )
        session.add(new_user)
        await session.commit()

    await state.clear()  # очищаем FSM
    await message.answer(
        f"Приятно познакомиться, {full_name}! 🎉\n"
        "Твоя стажировка начинается сегодня. Желаем успехов!"
    )
