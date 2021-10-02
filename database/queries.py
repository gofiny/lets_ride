from asyncpg import Connection, Pool
from datetime import date, datetime
from uuid import UUID

import my_exceptions
from .sql import tables
from my_exceptions import TooManyPhotos

from . import sql


def conn_transaction(func):
    """
    Take connection pool, acqure new connection and wrapped all queries in transaction
    """
    async def wrapper(db_pool: Pool, *args, **kwargs):
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                return await func(conn=conn, *args, **kwargs)
    return wrapper


@conn_transaction
async def init_database(conn: Connection):
    """
    Init tables in database. Run on startup application
    """
    for table in tables:
        await conn.execute(tables[table])


@conn_transaction
async def is_nickname_free(conn: Connection, nickname: str) -> bool:
    """
    Check nickname in database for free
    """
    if await conn.fetchval(sql.select_nickname, nickname):
        return False
    return True


@conn_transaction
async def create_user(
    conn: Connection, uuid: UUID, nickname: str, first_name: str,
    reg_time: datetime, born_date: date, gender: str,
    hashed_password: str, rate_uuid: UUID
):
    """
    create new user in database
    """
    await conn.execute(
        sql.create_user, uuid, nickname, first_name,
        reg_time, born_date, gender, hashed_password, rate_uuid
    )


@conn_transaction
async def create_session(
    conn: Connection, uuid: UUID, user_uuid: UUID,
    device_id: str, start_time: datetime, token: str
) -> str:
    """
    Checking existing sessions on this device, return if exists or create new
    """
    exists_token = await conn.fetchval(sql.get_session_token_by_device, user_uuid, device_id)
    if exists_token:
        return exists_token
    await conn.execute(sql.insert_session, uuid, user_uuid, device_id, start_time, token)
    return token


@conn_transaction
async def his_authorized(conn: Connection, user_uuid: UUID, device_id: str, token: str) -> bool:
    """
    Check user authorization
    """
    return await conn.fetchval(sql.select_session_token, user_uuid, device_id) == token


@conn_transaction
async def add_photo(conn: Connection, photos: tuple[tuple[UUID, str]], photo_type: str, subject_uuid: UUID):
    """Check user's uploaded photo count, if greater than 5 raise exception"""
    photos_count = await conn.fetchval(sql.select_photo_count.format(photo_type=photo_type), subject_uuid)
    if (photos_count + len(photos)) > 5:
        raise TooManyPhotos("Max count of photos 5!")
    await conn.executemany(sql.insert_photo.format(photo_type=photo_type), photos)


@conn_transaction
async def create_profile(
    conn: Connection,
    uuid: UUID,
    user_uuid: UUID,
    desired_gender: str,
    min_age: int,
    max_age: int,
    profile_type: int,
    vehicle_type: str
):
    """Create new profile for user with appropriate profile type"""
    profile_uuid = await conn.fetchval(sql.check_profile, user_uuid, profile_type)
    if profile_uuid:
        raise my_exceptions.ProfileAlreadyExists

    await conn.execute(sql.insert_profile,
                       uuid, user_uuid,
                       desired_gender,
                       min_age, max_age,
                       profile_type, vehicle_type)
