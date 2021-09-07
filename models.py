from pydantic import BaseModel
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
