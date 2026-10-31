from typing import Optional

from sqlmodel import Session, select

from app.models.redemption_claim import RedemptionClaim


class RedemptionClaimRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, claim: RedemptionClaim, *, commit: bool = True) -> RedemptionClaim:
        self.db.add(claim)
        if commit:
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            self.db.refresh(claim)
        return claim

    def get_by_id(self, claim_id: int) -> Optional[RedemptionClaim]:
        return self.db.get(RedemptionClaim, claim_id)

    def list_for_student(self, student_id: int) -> list[RedemptionClaim]:
        statement = (
            select(RedemptionClaim)
            .where(RedemptionClaim.student_id == student_id)
            .order_by(RedemptionClaim.claim_date.desc(), RedemptionClaim.id.desc())
        )
        return list(self.db.exec(statement).all())

    def list_all(self) -> list[RedemptionClaim]:
        statement = select(RedemptionClaim).order_by(
            RedemptionClaim.claim_date.desc(), RedemptionClaim.id.desc()
        )
        return list(self.db.exec(statement).all())
