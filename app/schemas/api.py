"""Request/response bodies for the JSON API (``/api``)."""

from datetime import date as date_type
from typing import Literal, Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class LoginRequest(SQLModel):
    username: str
    password: str


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)


class VolunteerSessionCreate(SQLModel):
    description: str = Field(min_length=1, max_length=255)
    hours_logged: float = Field(gt=0, le=24)
    date: date_type


class VolunteerSessionReview(SQLModel):
    status: Literal["approved", "rejected"]


class VolunteerSessionResponse(SQLModel):
    id: int
    student_id: int
    description: str
    hours_logged: float
    date: date_type
    status: str


class AwardCreate(SQLModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=255)
    points_required: int = Field(ge=1)
    stock_quantity: int = Field(ge=0)


class AwardUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=255)
    points_required: Optional[int] = Field(default=None, ge=1)
    stock_quantity: Optional[int] = Field(default=None, ge=0)


class AwardResponse(SQLModel):
    id: int
    name: str
    description: str
    points_required: int
    stock_quantity: int


class RedemptionCreate(SQLModel):
    award_id: int


class RedemptionResponse(SQLModel):
    id: int
    student_id: int
    award_id: int
    claim_date: date_type
    status: str
