from aiogram import F, Router, types
from aiogram.types import ReplyKeyboardMarkup

from database.database import get_engine, get_session, get_sessionmaker
from keyboards.menu import admin_menu
from models.users import User
from settings.config import settings

router = Router()
engine = get_engine(settings.DATABASE_URL, echo=True)
session_factory = get_sessionmaker(engine)


# --------------------------
# Список пользователей
# --------------------------
@router.message(F.text == "👥 Пользователи")
async def list_users(message: types.Message):
    async with get_session(session_factory) as session:
        result = await session.execute(User.__table__.select())
        users = result.fetchall()

        if not users:
            await message.answer("❌ Пользователей пока нет.")
            return

        text = "👥 <b>Список пользователей:</b>\n\n"
        for u in users:
            text += f"ID: {u.id} | {u.full_name} | роль: {u.role}\n"

        # Кнопки по каждому пользователю
        keyboard = ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
        for u in users:
            keyboard.keyboard.append(
                [types.KeyboardButton(text=f"👤 Действия {u.id} — {u.full_name}")]
                + [[types.KeyboardButton(text="🏠 Главное меню")]]
            )

        await message.answer(
            text + "\nВыберите пользователя, чтобы изменить его роль или статус:",
            reply_markup=keyboard,
            parse_mode="HTML",
        )


# --------------------------
# Меню действий по пользователю
# --------------------------
@router.message(F.text.startswith("👤 Действия"))
async def user_action_menu(message: types.Message):
    try:
        user_id = int(message.text.split()[-1])  # "👤 Действия {id}"
    except (IndexError, ValueError):
        await message.answer("❌ Не удалось определить пользователя.")
        return

    async with get_session(session_factory) as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [types.KeyboardButton(text=f"🗑 Удалить {user.id}")],
                [types.KeyboardButton(text=f"✏️ Сменить роль {user.id}")],
                [types.KeyboardButton(text=f"🎓 Назначить стажировку {user.id}")],
                [
                    types.KeyboardButton(text="⬅️ Назад к пользователям"),
                    types.KeyboardButton(text="🏠 Главное меню"),
                ],
            ],
        )
        await message.answer(
            f"Выберите действие для <b>{user.full_name}</b>:",
            reply_markup=keyboard,
            parse_mode="HTML",
        )


# --------------------------
# Удаление пользователя
# --------------------------
@router.message(F.text.startswith("🗑 Удалить"))
async def delete_user(message: types.Message):
    try:
        user_id = int(message.text.split()[-1])
    except (IndexError, ValueError):
        await message.answer("❌ Неверный формат команды.")
        return

    async with get_session(session_factory) as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return
        await session.delete(user)
        await session.commit()
        await message.answer(f"✅ Пользователь {user.full_name} удалён.")


# --------------------------
# Смена роли пользователя
# --------------------------
@router.message(F.text.startswith("✏️ Сменить роль"))
async def change_role(message: types.Message):
    try:
        user_id = int(message.text.split()[-1])
    except (IndexError, ValueError):
        await message.answer("❌ Неверный формат команды.")
        return

    async with get_session(session_factory) as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        new_role = "admin" if user.role != "admin" else "employee"
        user.role = new_role
        await session.commit()
        await message.answer(f"✅ Роль пользователя {user.full_name} изменена на {new_role}.")


# --------------------------
# Назначение стажировки
# --------------------------
@router.message(F.text.startswith("🎓 Назначить стажировку"))
async def assign_internship(message: types.Message, bot):
    try:
        user_id = int(message.text.split()[-1])
    except (IndexError, ValueError):
        await message.answer("❌ Неверный формат команды.")
        return

    async with get_session(session_factory) as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        user.role = "intern"
        await session.commit()

        # Приветственное сообщение
        await message.answer(f"✅ {user.full_name} теперь стажёр.")
        await bot.send_message(
            user.telegram_id,
            "👋 Привет! Рады приветствовать тебя в команде! "
            "Начни знакомство с нашей командой — вот первый материал 📘",
        )



@router.message(F.text == "⬅️ Назад к пользователям")
async def back_to_users(message: types.Message):
    await list_users(message)


@router.message(F.text == "🏠 Главное меню")
async def main_menu(message: types.Message):
    await message.answer("🏠 Главное меню:", reply_markup=admin_menu)