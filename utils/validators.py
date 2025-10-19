import re
from datetime import date
from typing import Optional

import dateparser


def validate_full_name(full_name: str) -> Optional[str]:
    """
    Проверяет ФИО: должно состоять из 2-3 слов, только буквы.
    Приводит каждое слово к капитализированной форме.
    """
    full_name = full_name.strip()
    parts = full_name.split()
    if len(parts) < 2 or len(parts) > 3:
        return None
    for part in parts:
        if not re.fullmatch(r"[А-Яа-яЁё-]+", part):
            return None
    return " ".join(part.capitalize() for part in parts)


def validate_dob(dob_str: str) -> Optional[date]:
    """
    Преобразует строку в дату и проверяет возраст 16-70 лет.
    Ожидается формат 'ДД.ММ.ГГГГ'.
    """
    try:
        dob = dateparser.parse(dob_str, languages=["ru"])
        if not dob:
            return None
        dob = dob.date()
        # проверка возраста
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 16 or age > 70:
            return None
        return dob
    except ValueError:
        return None
