from asyncpg import Pool
from database import queries
from datetime import datetime, date
from uuid import uuid4

import models
import my_exceptions


async def registration(db_pool: Pool, user: models.RegUser):
    if not await queries.is_nickname_free(db_pool=db_pool, nickname=user.nickname):
        raise my_exceptions.UserExists("User with the same nickname already registered")

    user_uuid = uuid4()
    rate_uuid = uuid4()
    reg_time = datetime.now()
    born_date = date.fromtimestamp(user.born_date)

    await queries.create_user(
        db_pool=db_pool, uuid=user_uuid, nickname=user.nickname,
        first_name=user.first_name, reg_time=reg_time, born_date=born_date,
        gender=user.gender, rate_uuid=rate_uuid
    )
