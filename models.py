from pydantic import BaseModel
from fastapi import Query
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"


class RegUser(BaseModel):
    nickname: str = Query(
        None,
        min_length=3,
        max_length=35
    )
    first_name: str = Query(
        None,
        min_length=2,
        max_length=35
    ),
    born_date: int
    gender: Gender