from sqlalchemy import select
import asyncio
from passlib.context import CryptContext

from app.db.session import SessionDep
from app.models.user import UserModel
from app.schemas.user_add import UserAddSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD:
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_user_by_email(self, email: str) -> UserModel | None:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserAddSchema) -> UserModel:
        hashed_password = await asyncio.to_thread(pwd_context.hash, user_data.password)
        new_user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def verify_user(self, email: str, password: str) -> UserModel | None:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        is_valid = await asyncio.to_thread(pwd_context.verify, password, user.hashed_password)
        return user if is_valid else None
