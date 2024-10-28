import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select

# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/name_db"
# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/fastapidb"   # for local test
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db/fastapidb"  # for docker


Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    retries = 5
    for attempt in range(retries):
        try:
            async with engine.begin() as conn:
                # Создаем все таблицы, определенные в Base.metadata
                await conn.run_sync(Base.metadata.create_all)
            break
        except OperationalError:
            if attempt < retries - 1:
                await asyncio.sleep(2)  # Задержка между попытками
            else:
                raise


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def main():
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())
