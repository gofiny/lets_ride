from asyncpg import Pool
from config import STATIC_FILES, DOMAIN_NAME
from database import queries
from datetime import datetime, date
from fastapi import BackgroundTasks
from uuid import uuid4, UUID

import aiofiles
import models
import my_exceptions
import string
import secrets


def generate_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(secrets.choice(
        letters_and_digits) for _ in range(length))


def gen_files_uuid(files: list[bytes]) -> tuple[tuple[UUID, bytes]]:
    names = []
    for file in files:
        names.append((uuid4(), file))

    return tuple(names)


def gen_client_photos_name(files: tuple[tuple[UUID, bytes]]) -> list[str]:
    names = []
    for file in files:
        name = f"{DOMAIN_NAME}/{STATIC_FILES}/{file[0]}.jpg"
        names.append(name)
    return names


def pack_photo_to_upload(files: tuple[tuple[UUID, bytes]], subject_id: str) -> tuple[tuple[UUID, str]]:
    packed = []
    for file in files:
        packed.append((file[0], subject_id))

    return tuple(packed)


async def write_files(files: tuple[tuple[UUID, bytes]], file_extension: str):
    for file in files:
        async with aiofiles.open(f"{STATIC_FILES}/{file[0]}{file_extension}", "wb") as f:
            await f.write(file[1])


async def authorization(db_pool: Pool, user: models.AskAuthUser) -> str:
    session_id = uuid4()
    start_time = datetime.now()
    token = generate_string(64)

    token = await queries.create_or_get_session(
        db_pool=db_pool, session_id=session_id, user_id=user.user_id,
        device_id=user.device_id, start_time=start_time, token=token,
        hashed_password=user.hashed_password
    )

    return ".".join([token, user.user_id, user.device_id])


async def registration(db_pool: Pool, user: models.RegUser) -> UUID:
    if not await queries.is_nickname_free(db_pool=db_pool, nickname=user.nickname):
        raise my_exceptions.UserExists("User with the same nickname is already registered")

    user_id = uuid4()
    rating_id = uuid4()
    reg_time = datetime.now()
    born_date = date.fromtimestamp(user.born_date)

    await queries.create_user(
        db_pool=db_pool, user_id=user_id, nickname=user.nickname,
        first_name=user.first_name, reg_time=reg_time, born_date=born_date,
        gender=user.gender, hashed_password=user.hashed_password, rating_uuid=rating_id
    )

    return user_id


async def check_auth(db_pool: Pool, user_id: str, device_id: str, token: str):

    if not await queries.his_authorized(
        db_pool=db_pool, user_id=user_id,
        device_id=device_id, token=token
    ):
        raise my_exceptions.AuthError


async def upload_photos(
    db_pool: Pool,
    subject_id: str, photo_type: str,
    background_tasks: BackgroundTasks,
    photos: list[bytes]
) -> list[str]:

    if len(photos) > 5:
        raise my_exceptions.TooManyPhotos("You cannot upload more than 5 photos!")

    files = gen_files_uuid(files=photos)
    photos_to_upload = pack_photo_to_upload(files=files, subject_id=subject_id)

    await queries.add_photo(
        db_pool=db_pool, photos=photos_to_upload,
        photo_type=photo_type,
        subject_id=subject_id
    )

    background_tasks.add_task(write_files, files=files, file_extension=".jpg")

    return gen_client_photos_name(files=files)


async def create_profile(db_pool: Pool, profile: models.NewProfile):
    profile_id = uuid4()

    await queries.create_profile(
        db_pool=db_pool,
        profile_id=profile_id,
        user_id=profile.user_id,
        desired_gender=profile.desired_gender,
        min_age=profile.min_age,
        max_age=profile.max_age,
        profile_type=profile.profile_type,
        vehicle_type=profile.vehicle_type
    )
