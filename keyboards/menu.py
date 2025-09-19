from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# меню для сотрудника
employee_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Учебные материалы"), KeyboardButton(text="🍽️ Меню ресторана")],
        [KeyboardButton(text="📝 Тесты"), KeyboardButton(text="ℹ️ Контакты")]
    ],
    resize_keyboard=True
)

# меню для админа
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Учебные материалы"), KeyboardButton(text="🍽️ Меню ресторана")],
        [KeyboardButton(text="📝 Тесты"), KeyboardButton(text="ℹ️ Контакты")],
        [KeyboardButton(text="👥 Пользователи"), KeyboardButton(text="➕ Добавить материал")],
        [KeyboardButton(text="📊 Статистика")]
    ],
    resize_keyboard=True
)
