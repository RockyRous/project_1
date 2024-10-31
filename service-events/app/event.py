from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import random
from models import Event
import string


def generate_event_name(existing_names, length=8):
    """ Функция для генерации случайного уникального имени мероприятия """
    while True:
        name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if name not in existing_names:
            return name


async def create_unique_events(db: AsyncSession):
    """ Функция для добавления 10 уникальных мероприятий в базу данных """
    result = await db.execute(select(Event.name))
    existing_names = {row[0] for row in result.all()}

    events_to_add = []

    for _ in range(10):
        event_name = generate_event_name(existing_names)
        event_date = datetime.now() + timedelta(days=random.randint(1, 365))
        total_seats = random.randint(1, 5)

        event = Event(
            name=event_name,
            date=event_date,
            total_seats=total_seats,
            booked_seats=0
        )
        events_to_add.append(event)
        existing_names.add(event_name)

    db.add_all(events_to_add)
    await db.commit()