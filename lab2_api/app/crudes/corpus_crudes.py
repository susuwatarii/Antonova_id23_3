from sqlalchemy import select
from app.db.session import SessionDep
from app.models.corpus import CorpusModel
from app.schemas.corpus_add import CorpusAddSchema


class CorpusCRUD:
    def __init__(self, session: SessionDep):
        self.session = session

    async def create_corpus(self, corpus_data: CorpusAddSchema) -> CorpusModel:
        new_corpus = CorpusModel(
            corpus_name=corpus_data.corpus_name,
            text=corpus_data.text
        )
        self.session.add(new_corpus)
        await self.session.commit()
        await self.session.refresh(new_corpus)
        return new_corpus

    async def get_corpuses(self) -> list[CorpusModel]:
        result = await self.session.execute(select(CorpusModel))
        return result.scalars().all()

    async def get_corpus_by_id(self, corpus_id: int) -> CorpusModel | None:
        result = await self.session.execute(select(CorpusModel).where(CorpusModel.id == corpus_id))
        return result.scalar_one_or_none()
