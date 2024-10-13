from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.orm_query import orm_change_banner_image,orm_get_info_pages
from sqlalchemy.ext.asyncio import AsyncSession
from inlinekeyboars.inline_kbcreate import inkbcreate

admin_router = Router()
admin_list = ['civqw']
@admin_router.message(F.text.lower().contains('admin'))
async def admin_commnad(message: types.Message):
    if message.from_user.username in admin_list:
        await message.reply('йоу йоу йоу', reply_markup=inkbcreate(btns={
            'хуй': 'qwe',
            'Добавить/Изменить Баннер':  'banner',
            'Добавить начальную картинку': 'image'
        }, sizes=(2,)))
    else:
        await message.answer('ты не админ')

################# Микро FSM для загрузки/изменения баннеров ############################
class AddBanner(StatesGroup):
    image = State()

# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@admin_router.callback_query(StateFilter(None), F.data == ('banner'))
async def add_banner(cb: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await cb.message.answer(f"Отправьте фото баннера.\nВ описании укажите для какой страницы:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)

# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы по именам:
# main, catalog, cart(для пустой корзины), about, payment, shipping
@admin_router.message(AddBanner.image, F.photo)
async def add_banner1(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите коректное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()

# ловим некоррекный ввод
@admin_router.message(AddBanner.image)
async def add_banner2(message: types.Message):
    await message.answer("Отправьте фото баннера или напишите отмена")

