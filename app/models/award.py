from typing import Optional

from sqlmodel import Field, SQLModel


class AwardBase(SQLModel):
    name: str = Field(max_length=120)
    description: str = Field(max_length=255)
    points_required: int = Field(ge=1)
    stock_quantity: int = Field(ge=0)


class Award(AwardBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
