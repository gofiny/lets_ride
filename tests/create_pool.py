from asyncpg import create_pool
from config import DB_DESTINATION


async def get_pool():
    return await create_pool(DB_DESTINATION)
