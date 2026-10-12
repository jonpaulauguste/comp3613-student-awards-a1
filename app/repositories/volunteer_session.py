import logging
from datetime import date
from typing import Optional

from sqlmodel import Session, select

from app.models.volunteer_session import VolunteerSession

logger = logging.getLogger(__name__)


class VolunteerSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_for_student(
        self,
        *,
        student_id: int,
        description: str,
        hours_logged: float,
        session_date: date,
    ) -> VolunteerSession:
        session_row = VolunteerSession(
            student_id=student_id,
            description=description,
            hours_logged=hours_logged,
            date=session_date,
            status="pending",
        )
        try:
            self.db.add(session_row)
            self.db.commit()
            self.db.refresh(session_row)
            return session_row
        except Exception as exc:
            logger.error(f"An error occurred while saving volunteer session: {exc}")
            self.db.rollback()
            raise

    def list_for_student(self, student_id: int) -> list[VolunteerSession]:
        query = (
            select(VolunteerSession)
            .where(VolunteerSession.student_id == student_id)
            .order_by(VolunteerSession.date.desc(), VolunteerSession.id.desc())
        )
        return self.db.exec(query).all()

    def list_pending(self) -> list[VolunteerSession]:
        query = (
            select(VolunteerSession)
            .where(VolunteerSession.status == "pending")
            .order_by(VolunteerSession.date.asc(), VolunteerSession.id.asc())
        )
        return self.db.exec(query).all()

    def get_by_id(self, volunteer_session_id: int) -> Optional[VolunteerSession]:
        return self.db.get(VolunteerSession, volunteer_session_id)

    def save(self, volunteer_session: VolunteerSession) -> VolunteerSession:
        try:
            self.db.add(volunteer_session)
            self.db.commit()
            self.db.refresh(volunteer_session)
            return volunteer_session
        except Exception as exc:
            logger.error(f"An error occurred while updating volunteer session: {exc}")
            self.db.rollback()
            raise
