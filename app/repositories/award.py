from typing import Optional

from sqlmodel import Session, func, select

from app.models.award import Award
from app.models.redemption_claim import RedemptionClaim


class AwardRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Award]:
        statement = select(Award).order_by(Award.points_required.asc(), Award.id.asc())
        return list(self.db.exec(statement).all())

    def get_by_id(self, award_id: int) -> Optional[Award]:
        return self.db.get(Award, award_id)

    def save(self, award: Award, *, commit: bool = True) -> Award:
        self.db.add(award)
        if commit:
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            self.db.refresh(award)
        return award

    def delete(self, award: Award) -> None:
        try:
            self.db.delete(award)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def count_claims(self, award_id: int) -> int:
        statement = select(func.count()).select_from(RedemptionClaim).where(
            RedemptionClaim.award_id == award_id
        )
        return self.db.exec(statement).one()
