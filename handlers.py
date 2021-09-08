from asyncpg import Pool
from config import STATIC_FILES, DOMAIN_NAME
from database import queries
from datetime import datetime, date
from fastapi import BackgroundTasks, UploadFile
from uuid import uuid4, UUID

import models
import my_exceptions
import string
import secrets


def generate_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(secrets.choice(
        letters_and_digits) for _ in range(length))


async def authorization(db_pool: Pool, user: models.AskAuthUser) -> str:
    uuid = uuid4()
    start_time = datetime.now()
    token = generate_string(64)

    token = await queries.create_session(
        db_pool=db_pool, uuid=uuid, user_uuid=user.uuid,
        device_id=user.device_id, start_time=start_time, token=token
    )

    return ".".join([token, user.uuid, user.device_id])


async def registration(db_pool: Pool, user: models.RegUser) -> UUID:
    if not await queries.is_nickname_free(db_pool=db_pool, nickname=user.nickname):
        raise my_exceptions.UserExists("User with the same nickname is already registered")

    user_uuid = uuid4()
    rate_uuid = uuid4()
    reg_time = datetime.now()
    born_date = date.fromtimestamp(user.born_date)

    await queries.create_user(
        db_pool=db_pool, uuid=user_uuid, nickname=user.nickname,
        first_name=user.first_name, reg_time=reg_time, born_date=born_date,
        gender=user.gender, hashed_password=user.hashed_password, rate_uuid=rate_uuid
    )

    return user_uuid


async def check_auth(db_pool: Pool, user_uuid: str, device_id: str, token: str):
    if not await queries.his_authorized(
        db_pool=db_pool, user_uuid=user_uuid,
        device_id=device_id, token=token
    ):
        raise my_exceptions.AuthError


async def upload_user_photo(
    db_pool: Pool, photo: UploadFile,
    user: models.User, background_tasks: BackgroundTasks
) -> str:
    uuid = uuid4()
    filename = f"{uuid}.jpg"

    await queries.add_user_photo(db_pool=db_pool, uuid=uuid, user_uuid=user.uuid)
    background_tasks.add_task(photo.write, f"{STATIC_FILES}/{filename}")

    return f"{DOMAIN_NAME}/{STATIC_FILES}/{filename}"
