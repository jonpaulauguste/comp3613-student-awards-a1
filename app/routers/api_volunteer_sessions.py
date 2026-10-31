from typing import Optional

from fastapi import status

from app.dependencies import AdminDep, AuthDep, SessionDep
from app.dependencies.auth import StudentDep
from app.repositories.user import UserRepository
from app.repositories.volunteer_session import VolunteerSessionRepository
from app.schemas.api import (
    VolunteerSessionCreate,
    VolunteerSessionResponse,
    VolunteerSessionReview,
)
from app.services.volunteer_session_service import VolunteerSessionService
from . import api_router


def _service(db) -> VolunteerSessionService:
    return VolunteerSessionService(VolunteerSessionRepository(db), UserRepository(db))


@api_router.get("/volunteer-sessions", response_model=list[VolunteerSessionResponse])
async def api_list_volunteer_sessions(
    user: AuthDep, db: SessionDep, status: Optional[str] = None
):
    """Students get their own sessions; admins get all (optionally ?status=pending)."""
    return _service(db).list_sessions_for(user, status)


@api_router.post(
    "/volunteer-sessions",
    response_model=VolunteerSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def api_log_volunteer_hours(
    payload: VolunteerSessionCreate, student: StudentDep, db: SessionDep
):
    return _service(db).log_hours(
        student_id=student.id,
        description=payload.description,
        hours_logged=payload.hours_logged,
        session_date=payload.date,
    )


@api_router.get(
    "/volunteer-sessions/{session_id}", response_model=VolunteerSessionResponse
)
async def api_get_volunteer_session(session_id: int, user: AuthDep, db: SessionDep):
    return _service(db).get_session_for(user, session_id)


@api_router.patch(
    "/volunteer-sessions/{session_id}", response_model=VolunteerSessionResponse
)
async def api_review_volunteer_session(
    session_id: int,
    payload: VolunteerSessionReview,
    admin: AdminDep,
    db: SessionDep,
):
    """Admin approves or rejects a pending session: {"status": "approved"|"rejected"}."""
    return _service(db).review_session(session_id, payload.status)
