from pydantic import BaseModel


class CorpusAddSchema(BaseModel):
    """Схема для добавления нового корпуса в бд """
    corpus_name: str
    text: str
