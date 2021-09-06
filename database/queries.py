from asyncpg import Connection, Pool
from datetime import date, datetime
from uuid import UUID
from .sql import tables
from . import sql


def conn_transaction(func):
    async def wrapper(db_pool: Pool, *args, **kwargs):
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                return await func(conn=conn, *args, **kwargs)
    return wrapper


@conn_transaction
async def init_database(conn: Connection):
    for table in tables:
        await conn.execute(tables[table])


@conn_transaction
async def is_nickname_free(conn: Connection, nickname: str) -> bool:
    if await conn.fetchval(sql.select_nickname, nickname):
        return False
    return True


@conn_transaction
async def create_user(
    conn: Connection, uuid: UUID, nickname: str, first_name: str,
    reg_time: datetime, born_date: date, gender: str, rate_uuid: UUID
):
    await conn.execute(sql.create_user, uuid, nickname, first_name, reg_time, born_date, gender, rate_uuid)
