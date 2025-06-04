from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class CorpusModel(Base):
    """Класс для таблицы корпусов в бд"""
    __tablename__ = "corpuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    corpus_name: Mapped[str]
    text: Mapped[str]
