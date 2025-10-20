from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data_bot.materials_dict import MATERIALS  # словарь вида {"Название": "URL"}

router = Router()


def get_materials_categories_kb() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с категориями учебных материалов.
    """
    buttons = [
        [InlineKeyboardButton(text=category, callback_data=f"material_cat:{category}")]
        for category in MATERIALS.keys()
    ]
    buttons.append(
        [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="back_main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "📚 Учебные материалы")
async def show_materials(message: types.Message):
    """
    Показывает список категорий учебных материалов.
    """
    await message.answer(
        "📘 Выберите категорию:", reply_markup=get_materials_categories_kb()
    )


@router.callback_query(F.data.startswith("material_cat:"))
async def show_material_link(callback: types.CallbackQuery):
    """
    Показывает ссылку на материал выбранной категории.
    """
    category = callback.data.split("material_cat:")[1]
    url = MATERIALS.get(category)

    if not url:
        await callback.answer("Материал не найден 😔", show_alert=True)
        return

    await callback.message.edit_text(
        f"📖 <b>{category}</b>\n\n"
        f"Ознакомиться с материалом можно по ссылке ниже 👇",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Перейти к материалу", url=url)],
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад", callback_data="back_to_materials"
                    )
                ],
            ]
        ),
    )


@router.callback_query(F.data == "back_to_materials")
async def back_to_materials(callback: types.CallbackQuery):
    """
    Возврат к списку категорий учебных материалов.
    """
    await callback.message.edit_text(
        "📘 Выберите категорию:", reply_markup=get_materials_categories_kb()
    )


@router.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    """
    Возврат в главное меню (например, ReplyKeyboardMarkup с командами).
    """
    await callback.message.delete()
    await callback.message.answer("📲 Главное меню открыто. Выберите действие.")
