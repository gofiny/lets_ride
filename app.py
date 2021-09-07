from asyncpg import create_pool
from fastapi import FastAPI
from database.queries import init_database

import uvicorn
import config
import handlers
import models
import my_exceptions


app = FastAPI()
local_storage = {}


@app.on_event("startup")
async def on_startup():
    db_pool = await create_pool(config.DB_DESTINATION)
    await init_database(db_pool=db_pool)
    local_storage["db_pool"] = db_pool


@app.on_event("shutdown")
async def on_shutdown():
    db_pool = local_storage["db_pool"]
    await db_pool.close()


@app.post("/registration")
async def registration(user: models.RegUser):
    try:
        user_uuid = await handlers.registration(db_pool=local_storage["db_pool"], user=user)
    except my_exceptions.UserExists as error:
        return {"status": False, "error": error.message}
    else:
        return {"status": True, "uuid": user_uuid}


@app.get("/authorization")
async def authorization(user: models.AskAuthUser):
    token = await handlers.authorization(db_pool=local_storage["db_pool"], user=user)
    return {"status": True, "token": token}


if __name__ == "__main__":
    uvicorn.run("app:app")
