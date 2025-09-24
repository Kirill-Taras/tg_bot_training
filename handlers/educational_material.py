from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data_bot.materials_dict import MATERIALS  # импортируем словарь материалов
from aiogram import Router, F, types


router = Router()


def get_materials_categories_kb() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с категориями учебных материалов.
    """
    buttons = []
    for category in MATERIALS.keys():
        buttons.append([InlineKeyboardButton(
            text=category,
            callback_data=f"material_cat:{category}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Главное меню", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_material_links_kb(category: str) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с ссылками на материалы выбранной категории.
    """
    buttons = []
    for item in MATERIALS[category]:
        buttons.append([InlineKeyboardButton(
            text=item["title"],
            url=item["url"]  # открытие внешней ссылки
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_materials")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "📚 Учебные материалы")
async def show_materials(message: types.Message):
    """
    Показывает список категорий учебных материалов.
    """
    await message.answer("Выберите категорию:", reply_markup=get_materials_categories_kb())


@router.callback_query(F.data.startswith("material_cat:"))
async def show_material_links(callback: types.CallbackQuery):
    """
    Показывает кнопки с ссылками на материалы выбранной категории.
    """
    category = callback.data.split("material_cat:")[1]
    await callback.message.edit_text(
        f"📄 Материалы по категории: {category}",
        reply_markup=get_material_links_kb(category)
    )


@router.callback_query(F.data == "back_to_materials")
async def back_to_materials(callback: types.CallbackQuery):
    """
    Возврат к списку категорий учебных материалов.
    """
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_materials_categories_kb()
    )
