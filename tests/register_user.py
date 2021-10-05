from handlers import registration
from models import RegUser, Gender, AskForAuthUser
from datetime import datetime
from create_pool import get_pool

import asyncio


birthday = datetime(1999, 7, 9)
male = Gender("male")
hashed_password = "8ea9c7b1333371918d1b23ee6e768077db28da162709007825a4c3ad4cdb47e1"
new_user = RegUser(
    nickname="test",
    first_name="test",
    hashed_password=hashed_password,
    born_date=int(birthday.timestamp()),
    gender=male
)


async def register_user() -> AskForAuthUser:
    pool = await get_pool()
    user_id = await registration(db_pool=pool, user=new_user)
    user = AskForAuthUser(user_id=user_id, device_id="test_device", hashed_password=hashed_password)
    return user


if __name__ == "__main__":
    asyncio.run(register_user())
