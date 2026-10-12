from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class VolunteerSessionBase(SQLModel):
    description: str = Field(max_length=255)
    hours_logged: float = Field(gt=0)
    date: date


class VolunteerSession(VolunteerSessionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    status: str = Field(default="pending", max_length=20)
