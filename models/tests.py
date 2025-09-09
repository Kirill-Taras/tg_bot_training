from __future__ import annotations
from typing import Optional, List
import json

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base


class Test(Base):
    """Вопросы для тестирования сотрудников"""
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String(300), nullable=False)
    options: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-строка со списком вариантов
    correct_options: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-строка со списком правильных

    related_material_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def get_options_list(self) -> List[str]:
        return json.loads(self.options)

    def get_correct_list(self) -> List[str]:
        return json.loads(self.correct_options)

    def __repr__(self) -> str:
        return f"<Test {self.id}: {self.question}>"

