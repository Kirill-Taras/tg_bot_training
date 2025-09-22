from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import json
import os

router = Router()

# Загружаем меню один раз при старте
with open("menu.json", "r", encoding="utf-8") as f:
    MENU = json.load(f)


def get_categories_kb():
    """Создает клавиатуру с категориями"""
    buttons = []
    for idx, cat in enumerate(MENU):
        buttons.append([InlineKeyboardButton(
            text=cat["category"],
            callback_data=f"cat:{idx}"  # используем индекс вместо полного названия
        )])
    buttons.append([InlineKeyboardButton(
        text="⬅️ Главное меню",
        callback_data="back_main"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_items_kb(category_idx: int):
    """Создает клавиатуру с блюдами выбранной категории"""
    buttons = []
    category = MENU[category_idx]
    for idx, item in enumerate(category["items"]):
        buttons.append([InlineKeyboardButton(
            text=item["title"],
            callback_data=f"item:{category_idx}_{idx}"  # индекс категории + индекс блюда
        )])
    # Кнопки навигации
    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_categories"
    )])
    buttons.append([InlineKeyboardButton(
        text="⬅️ Главное меню",
        callback_data="back_main"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "🍽️ Меню ресторана")
async def menu_restaurant(message: types.Message):
    """Показывает категории меню"""
    await message.answer("📂 Выберите категорию:", reply_markup=get_categories_kb())


@router.callback_query(F.data.startswith("cat:"))
async def show_items(callback: types.CallbackQuery):
    """Показывает блюда выбранной категории"""
    category_idx = int(callback.data.split(":")[1])
    category_name = MENU[category_idx]["category"]
    await callback.message.edit_text(
        f"🍴 {category_name}\nВыберите блюдо:",
        reply_markup=get_items_kb(category_idx)
    )


@router.callback_query(F.data.startswith("item:"))
async def show_item(callback: types.CallbackQuery):
    """Показывает карточку блюда"""
    category_idx, item_idx = map(int, callback.data.split(":")[1].split("_"))
    item = MENU[category_idx]["items"][item_idx]

    caption = (
        f"<b>{item['title']}</b>\n"
        f"<i>{item['desc']}</i>\n"
        f"🥄 {item['weight']}\n"
        f"💰 {item['price']} ₽"
    )
    photo_path = item.get("photo")
    if photo_path and os.path.exists(photo_path):
        await callback.message.answer_photo(
            FSInputFile(photo_path),
            caption=caption,
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(caption, parse_mode="HTML")


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: types.CallbackQuery):
    """Возврат к списку категорий"""
    await callback.message.edit_text("📂 Выберите категорию:", reply_markup=get_categories_kb())


@router.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.delete()
    await callback.message.answer("📲 Главное меню открыто. Выберите действие.")
