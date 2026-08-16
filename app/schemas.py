from datetime import datetime
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    done: bool
    created_at: datetime

    class Config:
        from_attributes = True
