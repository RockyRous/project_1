""" Сервис аунтефикации """
import uvicorn
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI

from auth import login_user, create_user
from database import get_db
from schemas import Login, Token, UserCreate
from database import init_db


app = FastAPI()


# Подключение к базе данных при запуске приложения
@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/login", response_model=Token)
async def login_for_access_token(login_data: Login, db: AsyncSession = Depends(get_db)):
    # Вызовем сервис для логина
    return await login_user(db, login_data.username, login_data.password)


# Для Authorize
@app.post("/token", response_model=Token)
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: AsyncSession = Depends(get_db)):
    return await login_user(db, form_data.username, form_data.password)


@app.post("/users/")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)


if __name__ == '__main__':
    uvicorn.run("main:app")



