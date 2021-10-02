from pydantic import BaseModel
from starlette.authentication import BaseUser
from fastapi import Query
from enum import Enum


class PhotoType(str, Enum):
    user = "user"
    profile = "profile"


class Gender(str, Enum):
    male = "male"
    female = "female"


class ProfileType(int, Enum):
    driver = 0
    companion = 1
    together = 2


class VehicleType(str, Enum):
    moto = "moto"
    car = "car"
    bike = "bike"
    scooter = "scooter"
    legs = "legs"


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


class NewProfile(BaseModel):
    user_uuid: str
    desired_gender: Gender
    min_age: int = Query(..., ge=16, le=100)
    max_age: int = Query(..., ge=16, le=100)
    profile_type: ProfileType
    vehicle_type: VehicleType


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
