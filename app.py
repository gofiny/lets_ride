from asyncpg import create_pool
from asyncpg.exceptions import PostgresError
from fastapi import FastAPI, BackgroundTasks, File
from fastapi.responses import JSONResponse
from database.queries import init_database
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request, HTTPConnection
from typing import Optional

import uvicorn
import config
import handlers
import models
import my_exceptions


app = FastAPI()
local_storage = {}


class Authentication(AuthenticationBackend):
    """Authentication middleware"""
    async def authenticate(self, request: HTTPConnection) -> Optional[tuple[AuthCredentials, models.User]]:

        #  check authenticate only in marked methods in config"
        if request.url.path in config.PUBLIC_METHODS:
            return
        try:
            token, user_id, device_id = request.headers["Authorization"].split(".")
            await handlers.check_auth(
                db_pool=local_storage["db_pool"], user_id=user_id,
                device_id=device_id, token=token
            )
        except (my_exceptions.AuthError, ValueError, KeyError):
            raise AuthenticationError()

        return AuthCredentials(["authenticated"]), models.User(user_id=user_id, device_id=device_id, token=token)


def auth_exception_handler(_: Request, _exc: AuthenticationError) -> JSONResponse:
    """Return Json response with message if user is not authenticated"""
    return JSONResponse(
        status_code=200,
        content={"status": False, "detail": "User is not authorized"}
    )


app.add_middleware(AuthenticationMiddleware, backend=Authentication(), on_error=auth_exception_handler)


@app.on_event("startup")
async def on_startup():
    """Do this when stating application"""
    db_pool = await create_pool(config.DB_DESTINATION)
    await init_database(db_pool=db_pool)
    local_storage["db_pool"] = db_pool


@app.on_event("shutdown")
async def on_shutdown():
    """Run when application is turning off"""
    db_pool = local_storage["db_pool"]
    await db_pool.close()


@app.post("/registration")
async def registration(user: models.RegUser):
    """New user registration method"""
    try:
        user_id = await handlers.registration(db_pool=local_storage["db_pool"], user=user)
    except my_exceptions.UserExists as exc:
        return {"status": False, "error": exc.message}
    else:
        return {"status": True, "user_id": user_id}


@app.get("/authorization")
async def authorization(user: models.AskAuthUser):
    """User authorization method"""
    try:
        token = await handlers.authorization(db_pool=local_storage["db_pool"], user=user)
    except PostgresError:
        return {"status": False, "detail": "Authorization error. Check user_id, device_id or hashed_password"}
    return {"status": True, "token": token}


@app.post("/upload_photo")
async def upload_photo(
    subject_id: str, photo_type: models.PhotoType,
    background_tasks: BackgroundTasks,
    photos: list[bytes] = File(..., media_type="image/jpeg", max_length=524288)
):
    """
    Can upload from 1 to 5 photos in one time.
    If user already have many photos, return error message
    """
    try:
        photo_url = await handlers.upload_photos(
            db_pool=local_storage["db_pool"],
            subject_id=subject_id, photo_type=photo_type,
            photos=photos, background_tasks=background_tasks
        )
    except my_exceptions.TooManyPhotos as exc:
        return {"status": False, "detail": exc.message}
    except PostgresError:
        return {"status": False, "detail": "Wrong subject_id"}

    return {"status": True, "photo_url": photo_url}


@app.post("/create_profile")   # check for sql injections
async def create_profile(profile: models.NewProfile):
    """Create new profile for search opponent"""
    try:
        await handlers.create_profile(db_pool=local_storage["db_pool"], profile=profile)
    except my_exceptions.ProfileAlreadyExists as exc:
        return {"status": False, "detail": exc.message}
    except PostgresError:
        return {"status": False, "detail": "Wrong user_id"}
    return {"status": True}


if __name__ == "__main__":
    uvicorn.run("app:app")
