from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from app.models.user import User
from app.models.volunteer_session import VolunteerSession
from app.repositories.user import UserRepository
from app.repositories.volunteer_session import VolunteerSessionRepository
from app.services.errors import (
    ConflictError,
    InvalidInputError,
    NotFoundError,
    PermissionDeniedError,
)

MAX_HOURS_PER_SESSION = 24
MAX_DESCRIPTION_LENGTH = 255
SESSION_STATUSES = ("pending", "approved", "rejected")


def points_for_hours(hours_logged: float) -> int:
    """1 point per hour, rounded half-up, never less than 1.

    Python's ``round`` uses banker's rounding (``round(0.5) == 0``,
    ``round(2.5) == 2``), which gave 0.5-hour sessions zero points and made
    approval fail.
    """
    rounded = int(Decimal(str(hours_logged)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return max(1, rounded)


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
        trimmed_description = (description or "").strip()
        if not trimmed_description:
            raise InvalidInputError("Description is required.")
        if len(trimmed_description) > MAX_DESCRIPTION_LENGTH:
            raise InvalidInputError(
                f"Description must be {MAX_DESCRIPTION_LENGTH} characters or fewer."
            )
        if hours_logged is None or hours_logged <= 0:
            raise InvalidInputError("Hours logged must be greater than zero.")
        if hours_logged > MAX_HOURS_PER_SESSION:
            raise InvalidInputError(
                f"Hours logged cannot exceed {MAX_HOURS_PER_SESSION} for one session."
            )
        if session_date > date.today():
            raise InvalidInputError("Session date cannot be in the future.")
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

    def list_sessions_for(
        self, user: User, status: Optional[str] = None
    ) -> list[VolunteerSession]:
        """Admins see every session; students only see their own."""
        if status is not None and status not in SESSION_STATUSES:
            raise InvalidInputError(
                f"Status must be one of: {', '.join(SESSION_STATUSES)}."
            )
        if user.role == "admin":
            return self.volunteer_session_repo.list_by_status(status)
        sessions = self.volunteer_session_repo.list_for_student(user.id)
        if status is not None:
            sessions = [s for s in sessions if s.status == status]
        return sessions

    def get_session_for(self, user: User, volunteer_session_id: int) -> VolunteerSession:
        volunteer_session = self._get_or_404(volunteer_session_id)
        if user.role != "admin" and volunteer_session.student_id != user.id:
            raise PermissionDeniedError("You can only view your own volunteer sessions.")
        return volunteer_session

    def approve_session(self, volunteer_session_id: int) -> VolunteerSession:
        volunteer_session = self._get_pending_or_raise(volunteer_session_id, "approved")
        # Points and status are committed together, so a failure leaves neither.
        self.user_repo.add_points(
            user_id=volunteer_session.student_id,
            points=points_for_hours(volunteer_session.hours_logged),
            commit=False,
        )
        volunteer_session.status = "approved"
        return self.volunteer_session_repo.save(volunteer_session)

    def reject_session(self, volunteer_session_id: int) -> VolunteerSession:
        volunteer_session = self._get_pending_or_raise(volunteer_session_id, "rejected")
        volunteer_session.status = "rejected"
        return self.volunteer_session_repo.save(volunteer_session)

    def review_session(self, volunteer_session_id: int, decision: str) -> VolunteerSession:
        if decision == "approved":
            return self.approve_session(volunteer_session_id)
        if decision == "rejected":
            return self.reject_session(volunteer_session_id)
        raise InvalidInputError("Decision must be 'approved' or 'rejected'.")

    def _get_or_404(self, volunteer_session_id: int) -> VolunteerSession:
        volunteer_session = self.volunteer_session_repo.get_by_id(volunteer_session_id)
        if volunteer_session is None:
            raise NotFoundError("Volunteer session not found.")
        return volunteer_session

    def _get_pending_or_raise(self, volunteer_session_id: int, target: str) -> VolunteerSession:
        volunteer_session = self._get_or_404(volunteer_session_id)
        if volunteer_session.status == target:
            raise ConflictError(f"Volunteer session has already been {target}.")
        if volunteer_session.status != "pending":
            verb = "approved" if target == "approved" else "rejected"
            raise ConflictError(f"Only pending volunteer sessions can be {verb}.")
        return volunteer_session
