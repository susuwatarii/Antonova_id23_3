from fastapi import FastAPI

from app.api.auth import auth_router
from app.api.corpus import corpus_router
from app.api.search import search_router
from app.api.user import user_router
# from app.db.base import Base
# from app.db.session import engine


app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(corpus_router)
app.include_router(search_router)

# создание миграции  (создание бд и таблиц в ней)
# alembic revision --autogenerate -m "Initial tables"
# Применение миграций
# alembic upgrade head

# @app.post("/setup_database")
# async def setup_database():  # создаем таблицу в бд
#     async with engine.begin() as conn:  # подключились к бд
#         await conn.run_sync(Base.metadata.drop_all)  # полностью очищаем базу данных
#         await conn.run_sync(Base.metadata.create_all)  # создаем все таблицы и столбцы
#         return {"ok": True}

# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True)
