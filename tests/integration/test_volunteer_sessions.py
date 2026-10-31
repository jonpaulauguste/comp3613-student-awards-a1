"""Integration tests: volunteer hours (log, approve, reject) with a real database."""

from datetime import date, timedelta

import pytest

from app.repositories.user import UserRepository
from app.repositories.volunteer_session import VolunteerSessionRepository
from app.services.errors import ConflictError
from app.services.volunteer_session_service import VolunteerSessionService
from tests.conftest import make_session, make_user

YESTERDAY = date.today() - timedelta(days=1)


def make_service(db):
    return VolunteerSessionService(VolunteerSessionRepository(db), UserRepository(db))


def test_log_hours(db, student):
    service = make_service(db)

    saved = service.log_hours(
        student_id=student.id,
        description="Library Tutoring",
        hours_logged=3,
        session_date=YESTERDAY,
    )

    assert saved.id is not None
    assert saved.status == "pending"
    assert saved.student_id == student.id
    assert service.get_student_sessions(student.id)[0].id == saved.id


def test_approve_session_awards_points(db, student):
    row = make_session(db, student, hours=3)

    make_service(db).approve_session(row.id)

    db.refresh(row)
    db.refresh(student)
    assert row.status == "approved"
    assert student.total_points == 3


def test_approve_half_hour_session(db, student):
    row = make_session(db, student, hours=0.5)
    make_service(db).approve_session(row.id)
    db.refresh(student)
    assert student.total_points == 1


def test_approve_session_twice(db, student):
    row = make_session(db, student, hours=4)
    service = make_service(db)
    service.approve_session(row.id)

    with pytest.raises(ConflictError):
        service.approve_session(row.id)

    db.refresh(student)
    assert student.total_points == 4


def test_reject_session(db, student):
    row = make_session(db, student, hours=5)

    make_service(db).reject_session(row.id)

    db.refresh(row)
    db.refresh(student)
    assert row.status == "rejected"
    assert student.total_points == 0


def test_reject_session_after_approval(db, student):
    row = make_session(db, student, hours=2)
    service = make_service(db)
    service.approve_session(row.id)
    with pytest.raises(ConflictError):
        service.reject_session(row.id)
    db.refresh(student)
    assert student.total_points == 2


def test_get_pending_sessions(db, student):
    pending = make_session(db, student, status="pending")
    make_session(db, student, status="approved")
    make_session(db, student, status="rejected")

    result = make_service(db).get_pending_sessions()

    assert [row.id for row in result] == [pending.id]


def test_student_sees_only_own_sessions(db, student):
    alice = make_user(db, "alice")
    mine = make_session(db, student)
    make_session(db, alice)

    result = make_service(db).list_sessions_for(student)

    assert [row.id for row in result] == [mine.id]
