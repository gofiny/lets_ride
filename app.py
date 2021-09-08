from asyncpg import create_pool
from asyncpg.exceptions import PostgresError
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from database.queries import init_database
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request, HTTPConnection

import uvicorn
import config
import handlers
import models
import my_exceptions


app = FastAPI()
local_storage = {}


class Authentication(AuthenticationBackend):
    async def authenticate(self, request: HTTPConnection):
        if request.url.path in config.PUBLIC_METHODS:
            return
        try:
            token, user_uuid, device_id = request.headers["Authorization"].split(".")
            await handlers.check_auth(
                db_pool=local_storage["db_pool"], user_uuid=user_uuid,
                device_id=device_id, token=token
            )
        except (my_exceptions.AuthError, ValueError, KeyError):
            raise AuthenticationError()

        return AuthCredentials(["authenticated"]), models.User(uuid=user_uuid, device_id=device_id, token=token)


def auth_exception_handler(_: Request, _exc: AuthenticationError):
    return JSONResponse(
        status_code=200,
        content={"status": False, "detail": "User is not authorized"}
    )


app.add_middleware(AuthenticationMiddleware, backend=Authentication(), on_error=auth_exception_handler)


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
    except my_exceptions.UserExists as exc:
        return {"status": False, "error": exc.message}
    else:
        return {"status": True, "uuid": user_uuid}


@app.get("/authorization")
async def authorization(user: models.AskAuthUser):
    try:
        token = await handlers.authorization(db_pool=local_storage["db_pool"], user=user)
    except PostgresError:
        return {"status": False, "detail": "Authorization error. Check uuid, device_id or hashed_password"}
    return {"status": True, "token": token}


@app.get("/request_auth")
async def request_auth():
    return {"status": False, "detail": "User is not authorized"}


@app.post("upload_user_photo")
async def upload_user_photo(
    request: Request, background_tasks: BackgroundTasks,
    photo: UploadFile = File(..., media_type="image/jpeg")
):
    try:
        photo_url = await handlers.upload_user_photo(
            db_pool=local_storage["db_pool"], photo=photo, user=request.user,
            background_tasks=background_tasks
        )
    except my_exceptions.TooManyPhotos as exc:
        return {"status": False, "detail": exc.message}

    return {"status": True, "photo_url": photo_url}


@app.get("/test_auth")
async def test_auth(user: models.AuthUser):
    return {"status": True, "user": user.uuid}


if __name__ == "__main__":
    uvicorn.run("app:app")
