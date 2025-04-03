from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class UserModel(Base):
    """Класс для таблицы пользователей в бд"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
