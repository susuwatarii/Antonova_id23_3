import jwt
from fastapi import APIRouter, Depends
from fastapi import Request
import asyncio

from app.core.config import config, security
from app.crudes.user_crudes import UserCRUD
from app.db.session import SessionDep


user_router = APIRouter()


@user_router.get(
    "/users/me",
    summary="Получает информацию о текущем пользователе",
    dependencies=[Depends(security.access_token_required)]
)
async def read_users_me(session: SessionDep, request: Request):
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    curr_user_id = await asyncio.to_thread(jwt.decode, token,
                                           key=config.JWT_SECRET_KEY,
                                           algorithms=[config.JWT_ALGORITHM])
    crud = UserCRUD(session)
    user = await crud.get_user_by_id(curr_user_id.get("sub"))
    return {"id": user.id,
            "email": user.email}
