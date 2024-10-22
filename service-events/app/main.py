""" Сервис мероприятий """
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Event(BaseModel):
    id: int
    name: str
    date: str

events_db = [
    {"id": 1, "name": "Event One", "date": "2024-12-01"},
    {"id": 2, "name": "Event Two", "date": "2024-12-15"}
]

@app.get("/events")
async def list_events():
    return events_db

@app.post("/events")
async def create_event(event: Event):
    events_db.append(event.dict())
    return event


if __name__ == '__main__':
    uvicorn.run("main:app")
