from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Catalog, Admins, Banner, Promokodes, Spam, Users

############### Работа с баннерами (информационными страницами) ###############

async def orm_add_banner_description(session: AsyncSession, data: dict):
    #Добавляем новый или изменяем существующий по именам
    #пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


############### Работа с каталогами##############

async def orm_check_catalog(session: AsyncSession):
    query = select(Catalog)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_chek_promo(session: AsyncSession, promo:str):
    query = select(Promokodes).where(Promokodes.promocode == promo)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_chek_users(session:AsyncSession, useid: str):
    query = select(Users).where(Users.user_id == useid)
    result  = await session.execute(query)
    return result.scalars().all()

async def orm_chek_users1(session:AsyncSession):
    query = select(Users.user_id)
    result  = await session.execute(query)
    return result.scalars().all()

async def orm_check_catalog_categ(session: AsyncSession):
    query = select(Catalog.categ)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_category(session:AsyncSession, game_cat:str):
    query = select(Catalog).where(Catalog.categ == game_cat)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_spam(session:AsyncSession):
    query = select(Spam.smska)
    result = await session.execute(query)
    return result.scalars().first()

async def orm_change_account(session: AsyncSession, account_name:str):
    query = select(Catalog).where(Catalog.name == account_name)
    result = await session.execute(query)
    return result.scalars().one_or_none()

async def orm_select_tovar(session: AsyncSession, tovar:str):
    query = select(Catalog).where(Catalog.name == tovar)
    result = await session.execute(query)
    return result.scalars().first()

async def orm_del_account(session: AsyncSession, desc_name : str):
    query = delete(Catalog).where(Catalog.name ==desc_name)
    result = await session.execute(query)
    return result

async def orm_del_admin(session: AsyncSession, username_to_delete : str):
    query = delete(Admins).where(Admins.usernameadm == username_to_delete)
    result = await session.execute(query)
    return result

async def orm_update_catalog(session: AsyncSession, account_name : str, field_name: str, new_value: str ):
    query = update(Catalog).where(Catalog.description == account_name).values({field_name: new_value})
    result = await session.execute(query)
    return result
############### Работа с админским хендлером###############
async def orm_use_admin(session: AsyncSession):
    query = select(Admins)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_for_ETA(session: AsyncSession, username: str ):
    query = select(Admins).where(Admins.usernameadm == username)
    result = await session.execute(query)
    return result.scalars().first()





