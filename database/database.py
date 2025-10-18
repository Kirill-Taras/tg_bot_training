from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from settings.config import settings

Base = declarative_base()

def get_engine(url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(url, echo=echo, future=True)

def get_sessionmaker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@asynccontextmanager
async def get_session(session_factory: sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session

async def init_db(engine: AsyncEngine):
    """
    Создаёт все таблицы при первом запуске.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

engine = get_engine(settings.DATABASE_URL)
SessionLocal = get_sessionmaker(engine)