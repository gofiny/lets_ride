from asyncpg import Connection, Pool
from datetime import date, datetime
from uuid import UUID
from .sql import tables
from . import sql
from ..my_exceptions import TooManyPhotos


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
    reg_time: datetime, born_date: date, gender: str,
    hashed_password: str, rate_uuid: UUID
):
    await conn.execute(
        sql.create_user, uuid, nickname, first_name,
        reg_time, born_date, gender, hashed_password, rate_uuid
    )


@conn_transaction
async def create_session(
    conn: Connection, uuid: UUID, user_uuid: UUID,
    device_id: str, start_time: datetime, token: str
) -> str:
    exists_token = await conn.fetchval(sql.get_session_token_by_device, user_uuid, device_id)
    if exists_token:
        return exists_token
    await conn.execute(sql.create_session, uuid, user_uuid, device_id, start_time, token)
    return token


@conn_transaction
async def his_authorized(conn: Connection, user_uuid: UUID, device_id: str, token: str) -> bool:
    return await conn.fetchval(sql.select_session_token, user_uuid, device_id) == token


@conn_transaction
async def add_user_photo(conn: Connection, uuid: UUID, user_uuid: UUID):
    photos_count = await conn.fetchval(sql.select_user_photo_count, user_uuid)
    if photos_count == 5:
        raise TooManyPhotos("Max photos count is 5!")
    await conn.execute(sql.insert_user_photo, uuid, user_uuid)


@conn_transaction
async def add_profile_photo(conn: Connection, uuid: UUID, profile_uuid: UUID):
    photos_count = await conn.fetchval(sql.select_user_photo_count, profile_uuid)
    if photos_count == 3:
        raise TooManyPhotos("Max photos count is 3!")
    await conn.execute(sql.insert_profile_photo, uuid, profile_uuid)
