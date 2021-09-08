from pydantic import BaseModel
from starlette.authentication import BaseUser
from fastapi import Query
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"


class RegUser(BaseModel):
    nickname: str = Query(
        ...,
        min_length=3,
        max_length=35
    )
    first_name: str = Query(
        ...,
        min_length=2,
        max_length=35
    )
    hashed_password: str = Query(
        ...,
        min_length=32,
        max_length=128
    )
    born_date: int
    gender: Gender


class AskAuthUser(BaseModel):
    uuid: str
    device_id: str
    hashed_password: str


class AuthUser(BaseModel):
    uuid: str
    device_id: str


class User(BaseUser):
    def __init__(self, uuid: str, device_id: str, token: str):
        self.uuid = uuid
        self.device_id = device_id
        self.token = token

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.uuid

    @property
    def identity(self) -> str:
        return "user"
