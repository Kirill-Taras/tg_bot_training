from aiogram import Router, types, F
from database.database import get_session
from models.users import User  # предполагается, что User у тебя уже есть

router = Router()

@router.message(F.text == "👥 Пользователи")
async def list_users(message: types.Message):
    async for session in get_session():
        users = await session.execute(User.__table__.select())
        users = users.fetchall()
        if not users:
            await message.answer("❌ Пользователей пока нет.")
            return

        text = "👥 Список пользователей:\n\n"
        for u in users:
            text += f"ID: {u.id} | {u.full_name} | роль: {u.role}\n"
        text += "\nВведите ID пользователя, чтобы изменить или удалить:"
        await message.answer(text)

@router.message(lambda msg: msg.text.isdigit())
async def user_action_menu(message: types.Message):
    user_id = int(message.text)
    async for session in get_session():
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text=f"🗑 Удалить {user.full_name}")],
                [types.KeyboardButton(text=f"✏️ Сменить роль {user.full_name}")],
                [types.KeyboardButton(text=f"📅 Назначить стажировку {user.full_name}")],
            ],
            resize_keyboard=True
        )
        await message.answer(f"Выберите действие для {user.full_name}:", reply_markup=keyboard)

# обработчики действий
@router.message(F.text.startswith("🗑 Удалить"))
async def delete_user(message: types.Message):
    user_name = message.text.replace("🗑 Удалить ", "")
    async for session in get_session():
        user = await session.execute(User.__table__.select().where(User.full_name == user_name))
        user = user.scalar_one_or_none()
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return
        await session.delete(user)
        await session.commit()
        await message.answer(f"✅ Пользователь {user_name} удалён.")

# смена роли и назначение стажировки можно будет добавить следующими шагами
