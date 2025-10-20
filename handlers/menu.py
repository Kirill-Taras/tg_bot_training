from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select

from database.database import SessionLocal, get_session
from keyboards.menu import admin_menu, employee_menu
from models.users import User

router: Router = Router()


async def get_user_role(telegram_id: int) -> str | None:
    """
    Возвращает роль пользователя по его telegram_id.

    Args:
        telegram_id (int): Telegram ID пользователя.

    Returns:
        str | None: Роль пользователя ("admin", "employee" или None, если не найден).
    """
    async with get_session(SessionLocal) as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user: User | None = result.scalar_one_or_none()
        return user.role if user else None


@router.message(F.text == "/menu")
async def show_menu(message: Message) -> None:
    """
    Отображает главное меню в зависимости от роли пользователя.

    Args:
        message (Message): Сообщение от пользователя.
    """
    role = await get_user_role(message.from_user.id)

    if role == "admin":
        await message.answer("Главное меню (админ):", reply_markup=admin_menu)
    elif role == ["employee"]:
        await message.answer("Главное меню:", reply_markup=employee_menu)
    else:
        await message.answer("❌ Вы не зарегистрированы. Введите /start для начала.")


@router.message(F.text == "📝 Тесты")
async def tests(message: Message) -> None:
    """
    Заглушка для раздела тестов.

    Args:
        message (Message): Сообщение от пользователя.
    """
    await message.answer("📝 Здесь можно будет пройти тест.")


@router.message(F.text == "/myrole")
async def check_my_role(message: Message):
    async with get_session(SessionLocal) as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user: User | None = result.scalar_one_or_none()
        if user:
            await message.answer(f"👤 Ваша роль: {user.role}")
        else:
            await message.answer("❌ Вы не зарегистрированы.")


@router.message(F.text == "/delete_me")
async def delete_me(message: Message):
    async with get_session(SessionLocal) as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()
            await message.answer(
                "🗑️ Ваш аккаунт удалён. Введите /start для повторной регистрации."
            )
        else:
            await message.answer("❌ Вас и так нет в базе.")
