from fastapi import APIRouter, Depends, HTTPException
from app.core.config import security
from app.crudes.corpus_crudes import CorpusCRUD
from app.db.session import SessionDep
from app.schemas.search_info import SearchInfo
from app.celery.tasks import search_task
from app.celery.config import celery_app
from celery.result import AsyncResult


search_with_status_router = APIRouter()


@search_with_status_router.post(
    "/search_algorithm_with_status",
    summary="Нечеткий поиск через Celery",
    dependencies=[Depends(security.access_token_required)]
)
async def search_algorithm_with_status(search_info: SearchInfo, session: SessionDep):
    crud = CorpusCRUD(session)
    corpus = await crud.get_corpus_by_id(search_info.corpus_id)
    if corpus is None:
        raise HTTPException(status_code=404, detail=f"Corpus with id {search_info.corpus_id} not found")

    # Запуск задачи Celery
    # через .delay() или .apply_async(), возвращаетcя AsyncResult, содержащий task_id
    task = search_task.delay(
        corpus_text=corpus.text,
        word=search_info.word,
        algorithm=search_info.algorithm
    )
    return {"task_id": task.id}


@search_with_status_router.get(
    "/search_status/{task_id}",  # task_id — path-параметр, который передаётся в URL
    summary="Статус поиска слова",
    dependencies=[Depends(security.access_token_required)]
)
async def get_search_status(task_id: str):
    # AsyncResult - объект-контейнер
    # с помощью которого можно проверять состояние задачи и получать результат
    task = AsyncResult(task_id, app=celery_app)


    if task.state == 'PENDING':
        # Воркер не запущен (или не подключён к брокеру Redis)
        # AsyncResult по несуществующему task_id
        # Redis backend недоступен - Celery не может записать состояние и результат
        # (например, путь к сокету /tmp/redis.sock больше не существует)
        return {"status": "PENDING"}
    elif task.state == 'FAILURE':
        return {"status": "FAILURE", "reason": str(task.info)}
    elif task.state == 'STARTED':
        return {"status": "STARTED", **task.info}  # (task.info or {}) — защита от None
    elif task.state == 'PROGRESS':
        return {"status": "PROGRESS", **task.info}
    elif task.state == 'SUCCESS':
        return {"status": "COMPLETED", **task.result}
    else:
        return {"status": task.state, "meta": task.info}