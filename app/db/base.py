import asyncio
import asyncpg

from app.db.models import CREATE_TABLES_SQL
from app.config import settings

pool: asyncpg.Pool | None = None


async def create_pool(max_retries: int = 10, delay: float = 1.5) -> asyncpg.Pool:
    global pool

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
                min_size=1,
                max_size=5,
                command_timeout=60,
                timeout=30,
            )
            return pool
        except Exception as e:
            last_error = e
            print(f"Попытка {attempt}/{max_retries} подключения к БД не удалась: {e}")
            await asyncio.sleep(delay)

    raise RuntimeError(f"Не удалось подключиться к PostgreSQL после {max_retries} попыток") from last_error


async def close_pool() -> None:
    global pool
    if pool:
        await pool.close()
        pool = None


def get_pool() -> asyncpg.Pool:
    if pool is None:
        raise RuntimeError("Database pool is not initialized")
    return pool


async def init_db() -> None:
    """Создаёт таблицы, если их ещё нет."""
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(CREATE_TABLES_SQL)
