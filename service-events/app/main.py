""" Сервис мероприятий """
import pika
import json
import os
import time

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import Event, Booking, User
from database import async_session, get_db
from event import create_unique_events

app = FastAPI()

# todo: Красиво спрятать
# RABBITMQ_URL = os.getenv("RABBITMQ_URL")
RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"

# Подключение к RabbitMQ
connection = None
retries = 5
for i in range(retries):
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        break
    except pika.exceptions.AMQPConnectionError:
        if i < retries - 1:
            time.sleep(2)  # Задержка перед следующей попыткой
        else:
            raise

# connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()
channel.exchange_declare(exchange='booking_events', exchange_type='fanout')


def send_booking_created_event(user_id, event_id):
    """ Функция для отправки события """
    event_data = {
        "user_id": user_id,
        "event_id": event_id
    }
    channel.basic_publish(exchange='booking_events', routing_key='', body=json.dumps(event_data))


# todo: Только по авторизации
@app.post("/events/{event_id}/book")
async def book_event(event_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """ Бронирование места """
    event = await db.execute(select(Event).filter(Event.id == event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event = event.first()

    if event.available_seats() <= 0:
        raise HTTPException(status_code=400, detail="No available seats")

    # Создаем бронирование и обновляем количество забронированных мест
    booking = Booking(user_id=user_id, event_id=event_id)
    db.add(booking)
    event.booked_seats += 1
    await db.commit()
    await db.refresh(event)

    # Отправляем событие в RabbitMQ
    send_booking_created_event(user_id, event_id)

    return {"message": "Booking successful"}


# todo: Только по авторизации
@app.get("/user/{user_id}/bookings")
async def get_user_bookings(user_id: int, db: AsyncSession = Depends(get_db)):
    """ Получение списка забронированных мероприятий для пользователя """
    try:
        # Используем асинхронный метод execute для запроса
        result = await db.execute(select(Booking).filter(Booking.user_id == user_id))
        bookings = result.scalars().all()  # Получаем все строки из результата
        return {"bookings": bookings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении бронирований: {str(e)}")


# todo: Только по авторизации
@app.post("/populate-events", response_model=dict)
def populate_events(db: AsyncSession = Depends(get_db)):
    try:
        create_unique_events(db)
        return {"status": "10 новых мероприятий добавлены в базу данных"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении мероприятий: {str(e)}")


# todo: Только по авторизации
@app.delete("/delete-all-events", response_model=dict)
async def delete_all_events(db: AsyncSession = Depends(get_db)):
    """Асинхронное удаление всех мероприятий из базы данных"""
    # Выполняем асинхронный запрос на удаление всех записей из таблицы Event
    await db.execute(delete(Event))
    await db.commit()  # Асинхронное подтверждение изменений в базе данных
    return {"status": "Все мероприятия удалены из базы данных"}
