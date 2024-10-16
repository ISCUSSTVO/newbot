from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime,  Text, func

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default = func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default = func.now() , onupdate= func.now())

##################Дтаблица админов################################################################
class Admins(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    usernameadm: Mapped[str] = mapped_column(String)
##################Дтаблица Юзеров################################################################
class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    user_id: Mapped[int] = mapped_column(Integer)
##################Дтаблица Юзеров################################################################
class Spam(Base):
    __tablename__ = 'rassilka'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    smska: Mapped[str] = mapped_column(String)
##################таблица аккаунтов################################################################aa
class Catalog(Base):
    __tablename__ = 'allacc'

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    description: Mapped[str] = mapped_column(String)
    categ: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[int]  = mapped_column(Integer)

##################таблица банеры ################################################################
class Banner(Base):
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

class Promokodes(Base):
    __tablename__ = 'promocodes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    promocode: Mapped[str] = mapped_column(String(15), unique=True)
    discount: Mapped[str] = mapped_column(Integer(), nullable=False)
