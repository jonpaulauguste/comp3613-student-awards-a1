from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class RedemptionClaimBase(SQLModel):
    student_id: int = Field(foreign_key="user.id")
    award_id: int = Field(foreign_key="award.id")
    claim_date: date = Field(default_factory=date.today)
    status: str = Field(default="submitted", max_length=30)


class RedemptionClaim(RedemptionClaimBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
