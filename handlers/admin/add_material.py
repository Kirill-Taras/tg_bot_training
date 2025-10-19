from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from database.database import get_session, get_engine, get_sessionmaker
from models.materials import Material
from settings.config import settings

router = Router()
engine = get_engine(settings.DATABASE_URL, echo=True)
session_factory = get_sessionmaker(engine)

class AddMaterialStates(StatesGroup):
    title = State()
    text = State()
    photo = State()
    link = State()
    positions = State()
    show_day = State()

@router.message(F.text == "➕ Добавить материал")
async def start_add_material(message: types.Message, state: FSMContext):
    await message.answer("Введите название материала:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddMaterialStates.title)

@router.message(AddMaterialStates.title)
async def get_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите основной текст материала (или '-' если пропустить):")
    await state.set_state(AddMaterialStates.text)

@router.message(AddMaterialStates.text)
async def get_text(message: types.Message, state: FSMContext):
    text = None if message.text.strip() == "-" else message.text
    await state.update_data(text=text)
    await message.answer("Пришлите фото (или '-' чтобы пропустить):")
    await state.set_state(AddMaterialStates.photo)

@router.message(AddMaterialStates.photo)
async def get_photo(message: types.Message, state: FSMContext):
    if message.photo:
        photo_file_id = message.photo[-1].file_id
        await state.update_data(photo_file_id=photo_file_id)
    else:
        await state.update_data(photo_file_id=None)
    await message.answer("Введите ссылку (или '-' если нет):")
    await state.set_state(AddMaterialStates.link)

@router.message(AddMaterialStates.link)
async def get_link(message: types.Message, state: FSMContext):
    link = None if message.text.strip() == "-" else message.text
    await state.update_data(link=link)
    await message.answer("Кому отправлять (введите должности через запятую):")
    await state.set_state(AddMaterialStates.positions)

@router.message(AddMaterialStates.positions)
async def get_positions(message: types.Message, state: FSMContext):
    await state.update_data(positions=message.text)
    await message.answer("Укажите день стажировки (1, 2 или 3):")
    await state.set_state(AddMaterialStates.show_day)

@router.message(AddMaterialStates.show_day)
async def get_show_day(message: types.Message, state: FSMContext):
    try:
        show_day = int(message.text)
        if show_day not in (1, 2, 3):
            raise ValueError
    except ValueError:
        await message.answer("Введите число 1, 2 или 3:")
        return

    data = await state.get_data()

    async with get_session(session_factory) as session:
        material = Material(
            title=data['title'],
            text=data.get('text'),
            photo_file_id=data.get('photo_file_id'),
            link=data.get('link'),
            positions=data.get('positions'),
            show_day=show_day
        )
        session.add(material)
        await session.commit()

    await message.answer("✅ Материал успешно добавлен!", reply_markup=None)
    await state.clear()
