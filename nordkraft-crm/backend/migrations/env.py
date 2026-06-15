from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import MetaData, pool
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.url import asyncpg_engine_options


# this is the Alembic Config object, which provides access to the values within
# the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Hand-written migrations only; avoid importing ORM models here so `alembic upgrade`
# does not depend on declarative mapper configuration.
target_metadata = MetaData()


def run_migrations_offline() -> None:
    url, _ = asyncpg_engine_options(settings.DATABASE_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    url, engine_kwargs = asyncpg_engine_options(settings.DATABASE_URL)
    connectable = create_async_engine(url, poolclass=pool.NullPool, **engine_kwargs)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

