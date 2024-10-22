""" Сервис уведомлений """
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Notification(BaseModel):
    user_id: int
    message: str

@app.post("/send-notification")
async def send_notification(notification: Notification):
    # Логика отправки уведомления
    return {"status": "Notification sent", "user_id": notification.user_id}


if __name__ == '__main__':
    uvicorn.run("main:app")
