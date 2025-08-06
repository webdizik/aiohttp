import datetime
import os

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")
POSTGRES_DB = os.getenv("POSTGRES_DB", "aiohttp")
POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")

PG_DSN = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    @property
    def id(self):
        return {"id": self.id}


class Author(Base):

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, unique=True)


class Post(Base):

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, unique=True)
    id_authors = mapped_column(Integer, ForeignKey("authors.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now()
        )

    @property
    def desc(self):
        return {
            "id": self.id,
            "title": self.title,
            "ad_author": self.ad_author,
            "creation_time": self.creation_time.strftime('%d.%m.%Y в %H:%M:%S'),
            }


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def clear_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_orm():
    await engine.dispose()