from typing import Optional

from sqlmodel import Session, select

from app.models.award import Award


class AwardRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Award]:
        statement = select(Award).order_by(Award.points_required.asc(), Award.id.asc())
        return list(self.db.exec(statement).all())

    def get_by_id(self, award_id: int) -> Optional[Award]:
        return self.db.get(Award, award_id)

    def save(self, award: Award) -> Award:
        self.db.add(award)
        self.db.commit()
        self.db.refresh(award)
        return award
