from handlers import authorization
from register_user import register_user
from models import AskForAuthUser
from typing import Optional
from create_pool import get_pool

import asyncio


async def authorize_user(user: Optional[AskForAuthUser] = None):
    if not user:
        user = await register_user()
    pool = await get_pool()
    token = await authorization(db_pool=pool, user=user)
    print(
        f"user_id: {user.user_id}\n"
        f"token: {token}"
    )


if __name__ == "__main__":
    asyncio.run(authorize_user())
