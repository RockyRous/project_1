""" Сервис аунтефикации """
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str
    full_name: str

users_db = {
    "user1": {
        "username": "user1",
        "email": "user1@example.com",
        "full_name": "User One",
    }
}

@app.post("/token")
async def login():
    # Логика для генерации токена
    return {"access_token": "fake-token"}

@app.get("/users/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token == "fake-token":
        return users_db["user1"]
    raise HTTPException(status_code=401, detail="Invalid token")


if __name__ == '__main__':
    uvicorn.run("main:app")
