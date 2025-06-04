import multiprocessing
import time
import uvicorn

from fastapi import FastAPI
from app.celery.tasks import search_task

from app.api.auth import auth_router
from app.api.corpus import corpus_router
from app.api.search import search_router
from app.api.user import user_router
from app.api.search_with_status import search_with_status_router

from app.celery.config import celery_app


app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(corpus_router)
app.include_router(search_router)
app.include_router(search_with_status_router)


# Функция запуска воркера
def start_celery_worker():
    celery_app.worker_main([
        'worker',  #  команда запустить worker-процесс
        '--loglevel=info',  # логгирование событий (полезно для отладки)
        '--pool=solo'  # обязательный параметр для запуска в WSL
    ])


if __name__ == '__main__':
    # Запуск воркера в отдельном процессе
    worker_process = multiprocessing.Process(target=start_celery_worker)
    worker_process.start()
    time.sleep(1)  # Подождать, пока воркер поднимется

    uvicorn.run("main:app", host="127.0.0.1", port=8000)
    # reload=True  - reload создаёт дочерний процесс:
    # ломает multiprocessing.Process(...), который исп-ся для запуска Celery
    # воркер перестаёт "видеть" свой backend


# Красным цветом в терминале (как видно на скриншоте) отображаются логи уровня INFO от Celery


# windows:
# создание миграции  (создание бд и таблиц в ней)
# alembic revision --autogenerate -m "Initial tables"
# Применение миграций
# alembic upgrade head

