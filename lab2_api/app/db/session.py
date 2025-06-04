from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os


load_dotenv()  # Загружаем переменные из .env


engine = create_async_engine(os.getenv("DATABASE_URL"))
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():  # некий генератор сессий, обычно одна сессия(транзакция) для выполнения работы одной ручки
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
