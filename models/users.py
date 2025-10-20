from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class UserStatus(str, Enum):
    """Статусы стажировки/работы сотрудника"""

    PENDING = "ожидание"  # ожидает подтверждения админа
    TRAINING = "стажировка"  # проходит обучение
    HIRED = "принят"  # принят на работу
    REJECTED = "не принят"  # не принят


class User(Base):
    """Модель сотрудника ресторана"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, doc="ID пользователя в Telegram"
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, doc="ФИО сотрудника"
    )
    role: Mapped[str] = mapped_column(
        String(100),
        default="employee",
        nullable=False,
        doc="Роль: admin / employee / intern",
    )
    position: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, doc="Должность"
    )
    dob: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, doc="Дата рождения"
    )
    telegram_username: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, doc="Имя в ТГ"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, doc="Телефон"
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, doc="Дата начала работы"
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} {self.full_name} ({self.role}, {self.status.value})>"
