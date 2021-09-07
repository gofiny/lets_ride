from asyncpg import create_pool
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    try:
        if request.url.path not in config.PUBLIC_METHODS:
            token = request.headers["Authorization"]
            data = await request.json()
            user_uuid = data["uuid"]
            device_id = data["device_id"]
            await handlers.check_auth(
                db_pool=local_storage["db_pool"], user_uuid=user_uuid,
                device_id=device_id, token=token
            )
    except (my_exceptions.AuthError, KeyError):
        return JSONResponse({"status": False, "detail": "User is not authorized"})

    return await call_next(request)


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


@app.get("/test_auth")
async def test_auth(user: models.AuthUser):
    return {"status": True, "user": user.uuid}


if __name__ == "__main__":
    uvicorn.run("app:app")
