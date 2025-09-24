from __future__ import annotations
from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base


class Material(Base):
    """Учебный материал с категорией, названием, ссылкой и фото"""
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, doc="Категория материала")
    title: Mapped[str] = mapped_column(String(200), nullable=False, doc="Название материала")
    link: Mapped[Optional[str]] = mapped_column(String(300), nullable=True, doc="Ссылка на источник материала")
    photo_file_id: Mapped[Optional[str]] = mapped_column(String(300), nullable=True, doc="file_id фотографии в Telegram")
    show_day: Mapped[int] = mapped_column(Integer, nullable=False, default=1, doc="День стажировки для показа материала")

    def __repr__(self) -> str:
        return f"<Material {self.title} ({self.category}, day {self.show_day})>"
