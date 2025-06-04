from pydantic import BaseModel, EmailStr


class UserAddSchema(BaseModel):
    """Схема для добавления нового пользователя в бд """
    email: EmailStr
    password: str
