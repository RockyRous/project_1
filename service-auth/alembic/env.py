from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import pool
from alembic import context

from app.database import Base, engine

config = context.config

target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    # Подключение к базе данных
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"), future=True, echo=True)

    async with connectable.connect() as connection:
        await connection.run_sync(context.configure, target_metadata=target_metadata, literal_binds=True, compare_type=True)

        async with connection.begin():
            await context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
