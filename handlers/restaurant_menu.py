import json

from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()

# Загружаем меню при старте
with open("menu.json", "r", encoding="utf-8") as f:
    MENU = json.load(f)


def get_main_menu_kb():
    """Главное ресторанное меню"""
    buttons = [
        [InlineKeyboardButton(text=cat["category"], callback_data=f"cat:{idx}")]
        for idx, cat in enumerate(MENU)
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subcategories_kb(category_idx: int):
    """Подкатегории выбранной категории"""
    category = MENU[category_idx]
    buttons = []

    for sub in category.get("subcategories", []):
        buttons.append([InlineKeyboardButton(text=sub["title"], url=sub["url"])])

    buttons.append(
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "🍽️ Меню ресторана")
async def show_main_menu(message: types.Message):
    """Показывает основное меню категорий"""
    await message.answer("📋 Выберите раздел:", reply_markup=get_main_menu_kb())


@router.callback_query(F.data.startswith("cat:"))
async def show_category(callback: types.CallbackQuery):
    """Показывает подкатегории или ссылку"""
    category_idx = int(callback.data.split(":")[1])
    category = MENU[category_idx]

    # Если есть подкатегории — показываем их
    if "subcategories" in category:
        await callback.message.edit_text(
            f"📖 {category['category']}",
            reply_markup=get_subcategories_kb(category_idx),
        )
    # Если подкатегорий нет — просто ссылка
    elif "url" in category:
        await callback.message.answer(f"🔗 {category['category']}: {category['url']}")


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: types.CallbackQuery):
    """Возврат к списку категорий"""
    await callback.message.edit_text(
        "📋 Выберите раздел:", reply_markup=get_main_menu_kb()
    )


@router.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    """Возврат в главное меню бота"""
    await callback.message.delete()
    await callback.message.answer("📲 Главное меню открыто. Выберите действие.")
