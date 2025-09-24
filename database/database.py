"""
Асинхронная обвязка для работы с базой данных через SQLAlchemy.
- создаёт AsyncEngine
- даёт factory для асинхронных сессий
- умеет инициализировать таблицы (Base.metadata.create_all)

Использование:
    engine = get_engine(DATABASE_URL)
    SessionLocal = get_sessionmaker(engine)
    await init_db(engine)  # создать таблицы (импортируй все модели до вызова)
    async with get_session(SessionLocal) as session:
        ... <-- работа с session
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Базовый класс для всех ORM-моделей.
# Модели (например models/user.py) должны импортировать Base из этого модуля:
#   from database import Base
Base = declarative_base()


def get_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    """
    Создаёт и возвращает AsyncEngine для указанного database_url.
    Для SQLite (aiosqlite) ожидается строка вида:
        sqlite+aiosqlite:///./data/db/bot.db
    Параметр echo=True включает лог SQL-запросов (полезно при отладке).
    """
    return create_async_engine(database_url, future=True, echo=echo)


def get_sessionmaker(engine: AsyncEngine) -> sessionmaker:
    """
    Возвращает настроенный sessionmaker, который создаёт AsyncSession.
    expire_on_commit=False удобен в web/bot-окружениях — объекты не "сбрасываются" после commit.
    """
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def get_session(session_factory: sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для сессий:
        async with get_session(SessionLocal) as session:
            await session.execute(...)
    Закрывает сессию автоматически после выхода.
    """
    async with session_factory() as session:  # type: AsyncSession
        try:
            yield session
        finally:
            # обычно session закрывается автоматически, но явно укажем на безопасность
            await session.close()


async def init_db(engine: AsyncEngine) -> None:
    """
    Создаёт таблицы в базе данных (Base.metadata.create_all).
    ВАЖНО: перед вызовом импортируй все модули с моделями, чтобы metadata содержала таблицы.
    Например:
        import models.user  # noqa: F401
        await init_db(engine)
    """
    # Открываем транзакцию DDL и применяем create_all синхронно через run_sync
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


engine: AsyncEngine = get_engine("sqlite+aiosqlite:///./data/db/bot.db", echo=True)

SessionLocal: sessionmaker = get_sessionmaker(engine)