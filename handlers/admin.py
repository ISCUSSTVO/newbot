from aiogram import types, Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.models import Admins, Promokodes, Catalog
from db.orm_query import orm_change_account, orm_change_banner_image, orm_check_catalog, orm_del_account, orm_for_ETA,orm_get_info_pages, orm_update_catalog, orm_use_admin
from sqlalchemy.ext.asyncio import AsyncSession
from inlinekeyboars.inline_kbcreate import inkbcreate

admin_router = Router()
admin_list = ['civqw']





####################################АВТОДОБАВЛЕНИЕ АДМИНА ИЗ ЛИСТА ADMINLIST####################################
@admin_router.message(Command('eta'))
async def Evry_Time_Adm(message: types.Message, session: AsyncSession):
    if message.from_user.username in admin_list:
        for username in admin_list:
            # Проверяем, существует ли уже этот юзер в базе данных
            existing_admin = await orm_for_ETA(session, username)
            
        if existing_admin is None:
            # Если пользователя нет в базе, добавляем его
            new_admin = Admins(usernameadm=username)
            session.add(new_admin)
            await session.commit()
            await message.answer(
                'Ты теперь админ'
            )
        else:
            await message.answer(
                'Ты и так админ '
        )
    else:
        await message.reply(
            'ты не админ'
        )
####################################АДМ МЕНЮ КОЛЛБЕК####################################

@admin_router.callback_query(F.data==('admin'))
async def admin_commands_cb(callback: types.CallbackQuery):
    await callback.message.answer(
        'Админ меню', reply_markup=inkbcreate(btns={
            'Внести товар в каталог': 'AddItem',
            'Удалить/изменить товар в каталоге': 'delItem',
            'Добавить/изменить банер':  'banner',
            'Создать рассылочное сообщение':    'create_rassilka',
            'отправить рассылку':   'do_rassilka'
        })
    )

    await callback.message.delete()

####################################АДМ МЕНЮ МСГ####################################
@admin_router.message(Command('ad'))
async def admin_commands_msg(message: types.Message, session: AsyncSession):
    adminlist = await orm_use_admin(session)
    admin_usernames = [admin.usernameadm for admin in adminlist]
    if message.from_user.username in admin_usernames:
        await message.answer(
                'Админ меню', reply_markup=inkbcreate(btns={
                'Внести товар в каталог': 'AddItem',
                'Удалить/изменить товар в каталоге': 'delItem',
                'Добавить/изменить банер':  'banner',
                'Создать промокод': 'promocode'
                }))
        await message.delete()
    else:
        await message.answer(
            'ты не админ'
        )
        await message.delete()

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
###############################################################################
class GetPromocode(StatesGroup):
    Promo = State()
    Disk = State()

@admin_router.callback_query(StateFilter(None),F.data == ('promocode'))
async def chek_promocode1(callback:types.CallbackQuery, state:FSMContext):
    await callback.message.answer("Введите промокод")
    await state.set_state(GetPromocode.Promo)

@admin_router.message(GetPromocode.Promo)
async def get_sam_promocode(message:types.Message,state: FSMContext):
    await state.update_data(promo = message.text)
    await message.answer("введи скидку промокода")
    await state.set_state(GetPromocode.Disk)
    
    
@admin_router.message(GetPromocode.Disk)
async def get_diskount(message: types.Message, session: AsyncSession, state: FSMContext,):
    await state.update_data(disc = message.text)
    data = await state.get_data()
    qwe = Promokodes(
        promocode = data['promo'],
        discount = data['disc']
    )
    session.add(qwe)
    promo = data['promo']
    await session.commit()
    await state.clear()
    await message.answer(
    f'Промокод принят: {promo}',
        reply_markup=inkbcreate(btns={
            'Ещё промокод?': 'promokod',
            'Админ меню': 'admin'
        })
    )

##################Добавление аккаунта################################################################
class PlussAccount(StatesGroup):
    name = State()
    desc = State()
    categories = State()
    price = State()

    texts = {
        'PlussAccount.name':    'Введите название заново',
        'PlussAccount.desc':    'Введите описание заново',
        'PlussAccount.categories':  'Введите категорию заново',
        'PlussAccount.priceacc':    'Введите цену заново',
    }

@admin_router.callback_query(F.data == ('AddItem'))
async def add_account(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Введи название товара'
    )
    await state.set_state(PlussAccount.name)

@admin_router.message(PlussAccount.name)
async def add_game_name(message: types.Message, state: FSMContext):
    await state.update_data(accname = message.text)
    await message.answer(
        'Введи описание'
    )
    await state.set_state(PlussAccount.desc)

@admin_router.message(PlussAccount.desc)
async def add_game_desc(message: types.Message, state: FSMContext):
    await state.update_data(accdesc=message.text)
    await message.reply(
        'Введи цену '
    )
    await state.set_state(PlussAccount.price)

@admin_router.message(PlussAccount.price)
async def add_priceacc(message: types.Message, state: FSMContext):
    await state.update_data(priceacc=message.text)
    await message.reply(
        'Введи категорию '
    )
    await state.set_state(PlussAccount.categories)

@admin_router.message(PlussAccount.categories,)
async def add_categories(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(acccat=message.text)
    data = await state.get_data()

    newaccgame = Catalog(
        name = data['accname'],
        description=data['accdesc'],
        categ=data['acccat'],
        price=data['priceacc']
        
    )
    
    name = data['accname']
    price = data['priceacc']

    # Добавляем и коммитим в сессии базы данных
    session.add(newaccgame)
    await session.commit()
    await state.clear()

    # Отправляем изображение вместе с текстом
    await message.answer(
    f'Аккаунт добавлен\nОписание: {name}\nЦена: {price} rub',
        reply_markup=inkbcreate(btns={
            'Ещё аккаунт?': 'Plus_acc',
            'Админ меню': 'admin'
        })
    )

@admin_router.callback_query(F.data == 'delItem')
async def show_all_accounts(cb: types.CallbackQuery, session: AsyncSession):
    account_list = await orm_check_catalog(session)

    if account_list:
        for account in account_list:
            desc_name = account.name
            account_info = (
                f"Аккаунт: {desc_name}\n"
                f"Цена: {account.price}"
            )
            reply_markup = inkbcreate(btns={
                f'Изменить {desc_name}': f'chgacc_{desc_name}',
                f'Удалить {desc_name}': f'delacc_{desc_name}'
            })
            await cb.message.answer(account_info, reply_markup=reply_markup)
            await cb.message.delete()
    else:
        await cb.message.answer(
            'Нет аккаунтов, братик', reply_markup=inkbcreate(btns={
                'В меню': 'admin'
            })
        )
        await cb.message.delete()

##################Удаление аккаунта ################################################################
@admin_router.callback_query(F.data.startswith('delacc_'))
async def delete_acc(cb: types.CallbackQuery, session: AsyncSession):
    desc_name = cb.data.split('_')[1]
    await orm_del_account(session, desc_name)
    await session.commit()
    await cb.message.answer(f'Аккаунт {desc_name} удалён.')
    await cb.message.delete()

###СМЕНА ИНФОРМАЦИИ ОБ АКАУНТЕ###
@admin_router.callback_query(F.data.startswith('chgacc_'))
async def chng_acc(cb: types.CallbackQuery, session: AsyncSession):
    _, account_name = cb.data.split('_')
    account = await orm_change_account(session, account_name)
    
    await cb.message.answer(
        f"Вы выбрали аккаунт: {account.name}\n"
        f"Цена: {account.price}\n\n"
        "Что вы хотите изменить?",
        reply_markup=inkbcreate(btns={
            "Изменить название": f"change_name_{account_name}",
            "Изменить цену": f"change_price_{account_name}",
            "Изменить описание": f"change_description_{account_name}",
            "Изменить категории": f"change_categories_{account_name}",
        })
    )
    
    await cb.answer()


###СМЕНА ИНФОРМАЦИИ ОБ АКАУНТЕ КОНКРЕТНО ПО ПУНКТАМ###
@admin_router.callback_query(F.data.startswith('change_'))
async def process_change_selection(cb: types.CallbackQuery, state: FSMContext):
    _, change_type, account_name = cb.data.split('_')

    # Сохраняем имя аккаунта в состоянии
    await state.update_data(account_name=account_name)

    prompts = {
        'name': "Введите новое название:",
        'price': "Введите новую цену:",
        'description': "Введите новое описание:",
        'categories': "Введите новые категории",
    }

    if change_type in prompts:
        await cb.message.answer(prompts[change_type])
        await state.set_state(f"new_{change_type}")


@admin_router.message(StateFilter("new_name"))
async def update_games(message: types.Message, state: FSMContext, session: AsyncSession):
    await update_account_field(message, state, 'name', session)

@admin_router.message(StateFilter("new_price"))
async def update_price(message: types.Message, state: FSMContext, session: AsyncSession):
    await update_account_field(message, state, 'price', session)

@admin_router.message(StateFilter("new_description"))
async def update_description(message: types.Message, state: FSMContext, session: AsyncSession):
    await update_account_field(message, state, 'description', session)

@admin_router.message(StateFilter("new_categories"))
async def update_categories(message: types.Message, state: FSMContext, session: AsyncSession):
    await update_account_field(message, state, 'categories', session)

async def update_account_field(message: types.Message, state: FSMContext, field_name: str, session: AsyncSession):
    new_value = message.text
    user_data = await state.get_data()
    account_name = user_data.get('account_name')


    await orm_update_catalog(session, account_name, field_name, new_value)
    await session.commit()

    
    await message.answer(f"{field_name.replace('_', ' ').capitalize()} аккаунта обновлено на: {new_value}")
    await state.clear()


##################Назад к прошлому стейту, и отмена действия################################################################ 
@admin_router.message(F.text.casefold()==('назад'))
async def backstep(msg: types.Message,state: FSMContext):
    curstate = await state.get_state()
    if curstate == PlussAccount.name:
        await msg.answer(
            'Предыдущего шага нет'
        )
        return
    prev = None
    for step in PlussAccount.__all_states__:
        if step.state == curstate:
            await state.set_state(prev)
            await msg.answer(
                f"Вы вернулись к предыдущему шагу\n{PlussAccount.texts[prev.state]}"
            )
        prev = step

@admin_router.message(StateFilter('*'), F.text.casefold()==('отмена'))
async def cancel_hand(msg: types.Message, state: FSMContext):
    curstate = await state.get_state()
    if curstate is None:
        return
    await state.clear()
    await msg.answer('Отмена действия',reply_markup=inkbcreate(btns={
        'меню': 'admin'
    }))

