from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# меню для сотрудника
employee_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Учебные материалы"), KeyboardButton(text="🍽️ Меню ресторана")],
        [KeyboardButton(text="ℹ️ Контакты")]
    ],
    resize_keyboard=True
)

# меню для админа
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Учебные материалы"), KeyboardButton(text="🍽️ Меню ресторана")],
        [KeyboardButton(text="👥 Пользователи"), KeyboardButton(text="ℹ️ Контакты"),
         KeyboardButton(text="➕ Добавить материал")],
    ],
    resize_keyboard=True
)
