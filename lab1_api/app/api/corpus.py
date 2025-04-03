from fastapi import APIRouter, Depends
from fastapi import HTTPException

from app.core.config import config, security
from app.crudes.corpus_crudes import CorpusCRUD
from app.db.session import SessionDep
from app.schemas.corpus_add import CorpusAddSchema


corpus_router = APIRouter()


@corpus_router.post(
    "/upload_corpus",
    summary="Добавляет корпуса",
    dependencies=[Depends(security.access_token_required)]
)
async def upload_corpus(data: CorpusAddSchema, session: SessionDep):
    crud = CorpusCRUD(session)
    try:
        new_corpus = await crud.create_corpus(data)
        return {"corpus_id": new_corpus.id,
                "message": "Corpus uploaded successfully"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@corpus_router.get(
    "/corpuses",
    summary="Получает корпуса",
    dependencies=[Depends(security.access_token_required)]
)
async def get_corpuses(session: SessionDep):
    crud = CorpusCRUD(session)
    corpuses = await crud.get_corpuses()
    return {"corpuses": [{"id": corpus.id, "corpus_name": corpus.corpus_name} for corpus in corpuses]}
