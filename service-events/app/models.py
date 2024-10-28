from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    date = Column(DateTime, index=True)  # Дата мероприятия
    total_seats = Column(Integer)  # Общее количество мест
    booked_seats = Column(Integer, default=0)  # Забронированные места

    def available_seats(self):
        return self.total_seats - self.booked_seats


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Ссылка на пользователя
    event_id = Column(Integer, ForeignKey("events.id"))  # Ссылка на событие


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
