import asyncpg
from app.db.base import get_pool


async def get_or_create_user(telegram_id: int) -> asyncpg.Record:
    pool = get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1",
            telegram_id
        )
        if user:
            return user

        user = await conn.fetchrow(
            """
            INSERT INTO users (telegram_id)
            VALUES ($1)
            RETURNING *
            """,
            telegram_id
        )
        return user
