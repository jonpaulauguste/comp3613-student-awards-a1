from sqlmodel import Session, select

from app.models.redemption_claim import RedemptionClaim


class RedemptionClaimRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, claim: RedemptionClaim) -> RedemptionClaim:
        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)
        return claim

    def list_for_student(self, student_id: int) -> list[RedemptionClaim]:
        statement = (
            select(RedemptionClaim)
            .where(RedemptionClaim.student_id == student_id)
            .order_by(RedemptionClaim.claim_date.desc(), RedemptionClaim.id.desc())
        )
        return list(self.db.exec(statement).all())
