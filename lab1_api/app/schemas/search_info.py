from typing import Literal
from pydantic import BaseModel


class SearchInfo(BaseModel):
    """Схема для проверки полученной информации о способе поиска"""
    word: str  # слово для поиска
    algorithm: Literal["levenshtein", "l", "damerau levenshtein", "dl"]  # название алгоритма поиска
    corpus_id: int  # id корпуса текста для поиска в нем
