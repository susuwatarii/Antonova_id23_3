from fastapi import APIRouter, Depends
from fastapi import HTTPException
import asyncio

from app.core.config import security
from app.crudes.corpus_crudes import CorpusCRUD
from app.db.session import SessionDep
from app.schemas.search_info import SearchInfo
from app.services.search_functions import search


search_router = APIRouter()


@search_router.post(
    "/search_algorithm",
    summary="Выполняет нечеткий поиск. Доступные алгоритмы поиска: \"levenshtein\" и \"damerau levenshtein\"",
    dependencies=[Depends(security.access_token_required)]
)
async def search_algorithm(search_info: SearchInfo, session: SessionDep):
    # выбираем нужный корпус
    crud = CorpusCRUD(session)
    corpus = await crud.get_corpus_by_id(search_info.corpus_id)
    if corpus is None:
        raise HTTPException(status_code=404, detail=f"Corpus with id {search_info.corpus_id} not found")

    # поиск
    exec_time, res_lst = await asyncio.to_thread(search, corpus.text.lower(), search_info.word.lower(), search_info.algorithm)
    sorted_res_lst = sorted(res_lst, key=lambda x: x['distance'])
    return {"execution_time (milliseconds) ": exec_time,
            "results": sorted_res_lst}
