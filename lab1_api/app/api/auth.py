from fastapi import APIRouter, HTTPException, Response
from passlib.context import CryptContext

from app.core.config import config, security
from app.crudes.user_crudes import UserCRUD
from app.db.session import SessionDep
from app.schemas.user_add import UserAddSchema

auth_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@auth_router.post(
    "/sign-up",
    summary="Проверяет, не зарегистрирован ли уже пользователь с таким email."
            "Если нет, создает нового пользователя и генерирует для него токен."
)
async def sign_up(credentials: UserAddSchema, response: Response, session: SessionDep):
    crud = UserCRUD(session)

    if await crud.get_user_by_email(credentials.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    try:
        new_user = await crud.create_user(credentials)
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

    token = security.create_access_token(uid=f"{new_user.id}")
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"id": new_user.id,
            "email": new_user.email,
            "token": token}


@auth_router.post(
    "/signin",
    summary="Проверяет существование пользователя с указанным email."
            "Проверяет правильность введенного пароля."
)
async def signin(credentials: UserAddSchema, response: Response, session: SessionDep):
    crud = UserCRUD(session)

    user = await crud.verify_user(credentials.email, credentials.password)
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Invalid email or password")

    token = security.create_access_token(uid=f"{user.id}")
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"id": user.id,
            "email": user.email,
            "token": token}
