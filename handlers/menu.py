from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from models.users import User
from database.database import get_session
from keyboards.menu import employee_menu, admin_menu

router: Router = Router()


async def get_user_role(telegram_id: int) -> str | None:
    """
    Возвращает роль пользователя по его telegram_id.

    Args:
        telegram_id (int): Telegram ID пользователя.

    Returns:
        str | None: Роль пользователя ("admin", "employee" или None, если не найден).
    """
    async with get_session() as session:
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
    elif role == "employee":
        await message.answer("Главное меню:", reply_markup=employee_menu)
    else:
        await message.answer("❌ Вы не зарегистрированы. Введите /start для начала.")


@router.message(F.text == "📚 Учебные материалы")
async def materials(message: Message) -> None:
    """
    Показывает список доступных учебных материалов.

    Args:
        message (Message): Сообщение от пользователя.
    """
    text: str = (
        "📚 Доступные материалы:\n\n"
        "1. Основы сервиса — [ссылка](https://example.com/doc1)\n"
        "2. Техника безопасности — [ссылка](https://example.com/doc2)\n"
        "3. Работа с гостями — [ссылка](https://example.com/doc3)"
    )
    await message.answer(text, disable_web_page_preview=True)


@router.message(F.text == "🍽️ Меню ресторана")
async def menu_restaurant(message: Message) -> None:
    """
    Выводит сообщение о меню ресторана.

    Args:
        message (Message): Сообщение от пользователя.
    """
    await message.answer("🍽️ Тут будут фото и описание блюд.")


@router.message(F.text == "📝 Тесты")
async def tests(message: Message) -> None:
    """
    Заглушка для раздела тестов.

    Args:
        message (Message): Сообщение от пользователя.
    """
    await message.answer("📝 Здесь можно будет пройти тест.")


@router.message(F.text == "ℹ️ Контакты")
async def contacts(message: Message) -> None:
    """
    Заглушка для раздела контактов.

    Args:
        message (Message): Сообщение от пользователя.
    """
    await message.answer("ℹ️ Контакты менеджера: Иван Иванов 📞 +7 900 123-45-67")
