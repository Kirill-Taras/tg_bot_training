from aiogram import F, Router, types

from database.database import get_engine, get_session, get_sessionmaker
from models.users import User
from settings.config import settings

router = Router()
engine = get_engine(settings.DATABASE_URL, echo=True)
session_factory = get_sessionmaker(engine)


# список пользователей
@router.message(F.text == "👥 Пользователи")
async def list_users(message: types.Message):
    async with get_session(session_factory) as session:
        users = await session.execute(User.__table__.select())
        users = users.fetchall()

        if not users:
            await message.answer("❌ Пользователей пока нет.")
            return

        text = "👥 <b>Список пользователей:</b>\n\n"
        for u in users:
            text += f"ID: {u.id} | {u.full_name} | роль: {u.role}\n"
        text += "\nВведите ID пользователя, чтобы изменить:"
        await message.answer(text, parse_mode="HTML")


# меню действий
@router.message(lambda msg: msg.text.isdigit())
async def user_action_menu(message: types.Message):
    user_id = int(message.text)
    async with get_session(session_factory) as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text=f"🗑 Удалить {user.full_name}")],
                [types.KeyboardButton(text=f"✏️ Сменить роль {user.full_name}")],
                [
                    types.KeyboardButton(
                        text=f"🎓 Назначить стажировку {user.full_name}"
                    )
                ],
            ],
            resize_keyboard=True,
        )
        await message.answer(
            f"Выберите действие для <b>{user.full_name}</b>:",
            reply_markup=keyboard,
            parse_mode="HTML",
        )


# удалить пользователя
@router.message(F.text.startswith("🗑 Удалить"))
async def delete_user(message: types.Message):
    name = message.text.replace("🗑 Удалить ", "")
    async with get_session(session_factory) as session:
        user = await session.execute(
            User.__table__.select().where(User.full_name == name)
        )
        user = user.scalar_one_or_none()
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return
        await session.delete(user)
        await session.commit()
        await message.answer(f"✅ Пользователь {name} удалён.")


# сменить роль
@router.message(F.text.startswith("✏️ Сменить роль"))
async def change_role(message: types.Message):
    name = message.text.replace("✏️ Сменить роль ", "")
    async with get_session(session_factory) as session:
        user = await session.execute(
            User.__table__.select().where(User.full_name == name)
        )
        user = user.scalar_one_or_none()
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        new_role = "admin" if user.role != "admin" else "employee"
        user.role = new_role
        await session.commit()
        await message.answer(f"✅ Роль пользователя {name} изменена на {new_role}.")


# назначить стажировку
@router.message(F.text.startswith("🎓 Назначить стажировку"))
async def assign_internship(message: types.Message, bot):
    name = message.text.replace("🎓 Назначить стажировку ", "")
    async with get_session(session_factory) as session:
        user = await session.execute(
            User.__table__.select().where(User.full_name == name)
        )
        user = user.scalar_one_or_none()
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        user.role = "intern"
        await session.commit()

        # приветственное сообщение
        await bot.send_message(
            user.telegram_id,
            "👋 Привет! Рады приветствовать тебя в команде! "
            "Начни знакомство с нашей командой — вот первый материал 📘",
        )

        await message.answer(f"✅ {name} теперь стажёр.")
