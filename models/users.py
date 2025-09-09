from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Optional

from sqlalchemy import Integer, String, Date, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base


class UserStatus(str, Enum):
    """Статусы стажировки/работы сотрудника"""
    PENDING = "ожидание"
    TRAINING = "стажировка"
    HIRED = "принят"
    REJECTED = "не принят"


class User(Base):
    """Модель сотрудника ресторана"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[UserStatus] = mapped_column(SQLEnum(UserStatus), default=UserStatus.PENDING)
    onboarding_day: Mapped[int] = mapped_column(Integer, default=0)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} {self.full_name} ({self.status.value})>"
