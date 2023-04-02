from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Sortings(BaseModel):
    id: int
    date: datetime


class Tag(BaseModel):
    id: int
    name: str


class Arts(BaseModel):
    id: int
    tags: Optional[List[Tag]] = []
    title: Optional[str] = None
    author: Optional[str] = None
    filename: str
    sorting_id: Sortings
