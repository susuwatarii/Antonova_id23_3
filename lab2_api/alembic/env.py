import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy.engine import Connection
from alembic import context

from app.db.base import Base
from app.db.session import engine

# ! Нужны для правильного создания бд, чтобы в ней создались эти таблицы:
from app.models.user import UserModel
from app.models.corpus import CorpusModel


config = context.config
load_dotenv()
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online():
    # Точка входа для онлайн-миграций.
    # Используется по умолчанию при выполнении Alembic-команд без --offline.
    # Запускает асинхронный event loop.
    asyncio.run(run_migrations_async())


async def run_migrations_async():
    # Устанавливает асинхронное соединение с БД.
    # Вызывает синхронную функцию do_run_migrations.
    # Закрывает соединение после выполнения.
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def do_run_migrations(connection: Connection):
    # Непосредственно выполняет миграции в транзакции.
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,  # для SQLite
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Offline migrations are disabled.")
else:
    run_migrations_online()
