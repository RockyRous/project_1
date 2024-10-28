""" Сервис мероприятий """
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Event, Booking, User
from database import SessionLocal, engine
import pika
import json
import os

app = FastAPI()

# ????
Event.metadata.create_all(bind=engine)

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

# Подключение к RabbitMQ
connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
channel = connection.channel()
channel.exchange_declare(exchange='booking_events', exchange_type='fanout')


# Зависимость для подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Функция для отправки события
def send_booking_created_event(user_id, event_id):
    event_data = {
        "user_id": user_id,
        "event_id": event_id
    }
    channel.basic_publish(exchange='booking_events', routing_key='', body=json.dumps(event_data))


# Бронирование места
@app.post("/events/{event_id}/book")
def book_event(event_id: int, user_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.available_seats() <= 0:
        raise HTTPException(status_code=400, detail="No available seats")

    # Создаем бронирование и обновляем количество забронированных мест
    booking = Booking(user_id=user_id, event_id=event_id)
    db.add(booking)
    event.booked_seats += 1
    db.commit()
    db.refresh(event)

    # Отправляем событие в RabbitMQ
    send_booking_created_event(user_id, event_id)

    return {"message": "Booking successful"}


# Получение списка забронированных мероприятий для пользователя
@app.get("/users/{user_id}/bookings")
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for user")

    return [{"event_id": booking.event_id} for booking in bookings]

