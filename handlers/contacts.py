from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select

from database.database import get_engine, get_session, get_sessionmaker
from models.users import User
from settings.config import settings

router = Router()
engine = get_engine(settings.DATABASE_URL, echo=True)
session_factory = get_sessionmaker(engine)


@router.message(F.text == "ℹ️ Контакты")
async def contacts(message: Message) -> None:
    """
    Отображает список зарегистрированных пользователей с контактами.
    """
    async with get_session(session_factory) as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

    if not users:
        await message.answer("ℹ️ Пока нет зарегистрированных пользователей.")
        return

    text_parts = ["ℹ️ Контакты сотрудников:\n"]
    for u in users:
        tg_link = (
            f"[ссылка](https://t.me/{u.telegram_username})"
            if getattr(u, "telegram_username", None)
            else "—"
        )
        text_parts.append(
            f"👤 *{u.full_name}*\n"
            f"📌 Должность: {u.position or '—'}\n"
            f"📞 Телефон: {u.phone or '—'}\n"
            f"🔗 Telegram: {tg_link}\n"
        )

    await message.answer(
        "\n".join(text_parts), disable_web_page_preview=True, parse_mode="Markdown"
    )
