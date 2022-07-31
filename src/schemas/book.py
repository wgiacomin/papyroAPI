from __future__ import annotations

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class BookBase(BaseModel):
    id: Optional[int] = None
    cover: Optional[str] = None
    book_title: Optional[str] = None
    author: Optional[List[str]] = None
    count: Optional[int] = None

    class Config:
        orm_mode = True


class UserBook(BaseModel):
    nickname: str
    photo: Optional[str] = 'https://uploads.sarvgyan.com/2014/03/image-unavailable.jpg'
    id: int


class Review(BaseModel):
    date: datetime
    likes: Optional[int] = 0
    comments: Optional[int] = 0
    rate: Optional[int] = None
    you_like: Optional[bool] = False
    text: str
    user: UserBook


class BookByID(BaseModel):
    id: Optional[int] = None
    identifier: Optional[str] = None
    cover: Optional[str] = None
    book_title: str
    rate: Optional[int]
    raters: Optional[int]
    description: str
    author: List[str]
    reviews: Optional[List[Review]] = []
    genre: Optional[List[str]] = None
    book_status_user: Optional[str] = None

    class Config:
        orm_mode = True


class BookByType(BaseModel):
    id: Optional[int] = None
    identifier: Optional[str] = None
    cover: Optional[str] = None
    book_title: str
    rate: Optional[int]
    author: List[str]

    class Config:
        orm_mode = True
