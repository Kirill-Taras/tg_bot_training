from aiogram import Router, types, F
from database.database import get_session, get_engine, get_sessionmaker
from models.materials import Material
from settings.config import settings

router = Router()
engine = get_engine(settings.DATABASE_URL, echo=True)
session_factory = get_sessionmaker(engine)

@router.message(F.text.lower() == "удалить материал")
async def list_materials(message: types.Message):
    async with get_session(session_factory) as session:
        materials = await session.execute(
            Material.__table__.select()
        )
        materials = materials.fetchall()
        if not materials:
            await message.answer("❌ Нет материалов для удаления.")
            return

        text = "📚 Список материалов:\n\n"
        for m in materials:
            text += f"ID: {m.id} | {m.title} (день {m.show_day})\n"
        text += "\nВведите ID материала, который хотите удалить:"
        await message.answer(text)

@router.message(lambda msg: msg.text.isdigit())
async def delete_material_by_id(message: types.Message):
    material_id = int(message.text)
    async with get_session(session_factory) as session:
        material = await session.get(Material, material_id)
        if not material:
            await message.answer("❌ Материал не найден.")
            return
        await session.delete(material)
        await session.commit()
        await message.answer(f"✅ Материал '{material.title}' удалён.")
