from datetime import date

from app.models.volunteer_session import VolunteerSession
from app.repositories.user import UserRepository
from app.repositories.volunteer_session import VolunteerSessionRepository


class VolunteerSessionService:
    def __init__(
        self,
        volunteer_session_repo: VolunteerSessionRepository,
        user_repo: UserRepository,
    ):
        self.volunteer_session_repo = volunteer_session_repo
        self.user_repo = user_repo

    def log_hours(
        self,
        *,
        student_id: int,
        description: str,
        hours_logged: float,
        session_date: date,
    ) -> VolunteerSession:
        trimmed_description = description.strip()
        if not trimmed_description:
            raise ValueError("Description is required.")
        if hours_logged <= 0:
            raise ValueError("Hours logged must be greater than zero.")
        return self.volunteer_session_repo.create_for_student(
            student_id=student_id,
            description=trimmed_description,
            hours_logged=hours_logged,
            session_date=session_date,
        )

    def get_student_sessions(self, student_id: int) -> list[VolunteerSession]:
        return self.volunteer_session_repo.list_for_student(student_id)

    def get_pending_sessions(self) -> list[VolunteerSession]:
        return self.volunteer_session_repo.list_pending()

    def approve_session(self, volunteer_session_id: int) -> VolunteerSession:
        volunteer_session = self.volunteer_session_repo.get_by_id(volunteer_session_id)
        if volunteer_session is None:
            raise ValueError("Volunteer session not found.")
        if volunteer_session.status == "approved":
            raise ValueError("Volunteer session has already been approved.")
        if volunteer_session.status != "pending":
            raise ValueError("Only pending volunteer sessions can be approved.")

        volunteer_session.status = "approved"
        self.volunteer_session_repo.save(volunteer_session)
        self.user_repo.add_points(
            user_id=volunteer_session.student_id,
            points=round(volunteer_session.hours_logged),
        )
        return volunteer_session
