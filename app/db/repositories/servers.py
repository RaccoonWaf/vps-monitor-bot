import asyncpg
from app.db.base import get_pool


async def add_server(
    user_id: int,
    ip: str,
    port: int,
    protocol: str = "other"
) -> asyncpg.Record:
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO servers (user_id, ip, port, protocol)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            user_id, ip, port, protocol
        )


async def get_user_servers(user_id: int) -> list[asyncpg.Record]:
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT * FROM servers
            WHERE user_id = $1
            ORDER BY created_at
            """,
            user_id
        )


async def delete_server(server_id: int, user_id: int) -> bool:
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            DELETE FROM servers
            WHERE id = $1 AND user_id = $2
            """,
            server_id, user_id
        )
        return result != "DELETE 0"


async def count_user_servers(user_id: int) -> int:
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM servers WHERE user_id = $1",
            user_id
        )
