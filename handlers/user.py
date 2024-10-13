from aiogram import types, Router, F
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.menu_proccesing import get_menu_content
#from aiogram.fsm.state import StatesGroup
from inlinekeyboars.inline_kbcreate import Menucallback, get_keyboard,inkbcreate_url
user_router = Router()

@user_router.message(F.text.lower().contains('start') | F.text.lower().contains('старт'))
@user_router.message(CommandStart())
async def start(message:types.Message):
    await message.answer('qwe', reply_markup=get_keyboard(btns={
        "тг канал📺",
        "меню",
        "🤓отзывы"
    }))
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

@user_router.message(F.text.lower().contains('menu') | F.text.lower().contains('меню'))
async def menu (message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
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




@user_router.message()
async def nullmessage(message: types.Message):
    await message.answer('напиши старт')