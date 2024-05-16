from typing import List
from pydantic import BaseModel
from datetime import date, time


class UserCreate(BaseModel):
    username: str
    password: str
    gotify_app_token: str
    alibaba_username: str
    alibaba_password: str
    license: str


class Terminal(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class Filter(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    origin_terminals: List[Terminal]
    dest_terminals: List[Terminal]
    # bus_type: List[BUSType] | None = None  # TODO[Feature]: bus type filter
    start_price: int | None = None
    end_price: int | None = None

    class Config:
        from_attributes = True


class FilterCreate(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    origin_terminals: List[int] = []
    dest_terminals: List[int] = []
    # bus_type: List[BUSType] | None = None  # TODO[Feature]: bus type filter
    start_price: int | None = None
    end_price: int | None = None

    class Config:
        from_attributes = True


class ObjectWithGotifyToken(BaseModel):
    gotify_app_token: str


class Pipeline(BaseModel):
    id: int
    desc: str
    date: date

    origin_terminal: Terminal
    dest_terminal: Terminal
    search_filter: Filter | None
    buy_filter: Filter | None
    owner: ObjectWithGotifyToken
    active: bool

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    username: str
    gotify_app_token: str
    alibaba_username: str
    pipelines: List[Pipeline]
    is_admin: bool

    class Config:
        from_attributes = True


class PipelineCreate(BaseModel):
    desc: str = ""
    date: date
    origin_terminal: str
    dest_terminal: str
    search_filter: FilterCreate | None = None
    buy_filter: FilterCreate | None = None


class License(BaseModel):
    id: int
    value: str
    used: bool

    class Config:
        from_attributes = True


class LicenseCreate(BaseModel):
    value: str


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str