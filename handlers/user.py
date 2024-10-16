from aiogram import types, Router, F
from aiogram.types import InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Users
from db.engine import AsyncSessionLocal
from db.orm_query import orm_chek_promo, orm_chek_users, orm_get_banner
from handlers.menu_proccesing import game_catalog, get_menu_content, zaglushka
#from aiogram.fsm.state import StatesGroup
from inlinekeyboars.inline_kbcreate import Menucallback, get_keyboard, inkbcreate,inkbcreate_url
user_router = Router()







@user_router.message(F.text.lower().contains('start') | F.text.lower().contains('старт'))
@user_router.message(CommandStart())
async def start(message:types.Message):
    async with AsyncSessionLocal as session:
        useid = message.from_user.id
        banner = await orm_get_banner(session, "start")
        result = await orm_chek_users(session, useid)

        if not result:
            add_in_Users = Users(user_id=useid)
            session.add(add_in_Users)
            await session.commit()
        
        kbds = get_keyboard(btns={
            "тг канал📺",
            "меню",
            "🤓отзывы"
        })      
        await message.answer_photo(photo=banner.image, caption=banner.description, reply_markup=kbds)

@user_router.message(F.text.lower().contains('тг '))
async def tgchennel(message: types.Message):
    await message.answer("Ссылочка внизу ⬇️", reply_markup=inkbcreate_url(btns={
        "нажми": "https://t.me/s/serega_pirat2"
    }))

@user_router.message(F.text.lower().contains('отзывы'))
async def otzivi(message: types.Message):
    await message.answer("https://vk.com/topic-214629131_49341013?offset=20", reply_markup=inkbcreate_url(btns={
        "Отзывы": "https://во-все-тяжкие.рф/episodes/3-season-10-series/"
    }))

@user_router.callback_query(F.data == 'menu')
@user_router.message(F.text.lower().contains('menu') | F.text.lower().contains('меню'))
async def menu_handler(message: types.Message | types.CallbackQuery, session: AsyncSession):
    # Проверяем, является ли входящий объект колбэком
    is_callback = isinstance(message, types.CallbackQuery)

    if is_callback:
        await message.answer("Загрузка главного меню...")  # Обязательно отвечаем на колбэк

    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")

    # Убедитесь, что media.media — это корректный тип
    if isinstance(media, InputMediaPhoto):
        if is_callback:
            await message.message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)
        else:
            await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)

@user_router.callback_query(Menucallback.filter())
async def user_manu(callback: types.CallbackQuery, callback_data: Menucallback, session: AsyncSession):

    result = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name
    )
    if result is None:
        await callback.answer("Не удалось получить данные.", show_alert=True)
        return
    media, reply_markup = result
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()

@user_router.callback_query(F.data.startswith('show_cat_'))
async def process_show_cat(callback_query: types.CallbackQuery, session: AsyncSession):
    # Извлекаем категорию из колбек-данных
    game_cat = callback_query.data.split('_')[-1]  # Получаем название категории
    media, kbds = await game_catalog(session, game_cat, level=2)
    # Отправляем сообщение пользователю
    await callback_query.message.edit_media(media=media, reply_markup=kbds)
    await callback_query.answer()

@user_router.callback_query(F.data.startswith('show_'))
async def process_show_game(callback_query: types.CallbackQuery, session: AsyncSession):
    # Извлекаем категорию из колбек-данных
    tovar = callback_query.data.split('_')[-1]  # Получаем название категории
    media, kbds = await zaglushka(session, tovar, level=3)
    # Отправляем сообщение пользователю
    await callback_query.message.edit_media(media=media, reply_markup=kbds)
    await callback_query.answer()
###########################Получение промокода################
class GetPromo(StatesGroup):
    Promo = State()

@user_router.callback_query(F.data == ('promo'))
async def chek_promocode(callback:types.CallbackQuery, state:FSMContext, session: AsyncSession, level = 3):
    banner = await orm_get_banner(session, "catalog")
    image = None
    if banner:
        image = InputMediaPhoto(
            media=banner.image,
            caption="\nВведите промокод"
        )
    await callback.message.edit_media(media=image, reply_markup=inkbcreate(btns={
        'отмена':    Menucallback(level=level -2, menu_name='game_catalog').pack()
    }))
    await state.set_state(GetPromo.Promo)
    #await callback.message.delete()

@user_router.message(GetPromo.Promo)
async def get_promocode(message:types.Message, session: AsyncSession):
    promo = message.text
    result = await orm_chek_promo(session, promo)
    if result:
        await message.answer('Промокод принят')
        return
    else:
        await message.answer('Нет такого промокода', reply_markup=inkbcreate(btns={
            'В меню':   'menu'
        }))
        return





@user_router.message()
async def nullmessage(message: types.Message):
    await message.answer('напиши старт')