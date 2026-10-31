"""Unit tests: VolunteerSessionService with mocked repositories (no database)."""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from app.models.user import User
from app.models.volunteer_session import VolunteerSession
from app.services.errors import (
    ConflictError,
    InvalidInputError,
    NotFoundError,
    PermissionDeniedError,
)
from app.services.volunteer_session_service import (
    VolunteerSessionService,
    points_for_hours,
)

YESTERDAY = date.today() - timedelta(days=1)


def make_service():
    session_repo = MagicMock()
    user_repo = MagicMock()
    return VolunteerSessionService(session_repo, user_repo), session_repo, user_repo


def new_session(hours=3.0, status="pending", student_id=7):
    return VolunteerSession(
        id=10,
        student_id=student_id,
        description="Beach Cleanup",
        hours_logged=hours,
        date=YESTERDAY,
        status=status,
    )


def new_user(user_id, role="regular_user"):
    return User(
        id=user_id,
        username="user" + str(user_id),
        email="user" + str(user_id) + "@example.com",
        password="x",
        role=role,
    )


# ---- points_for_hours ----

def test_points_for_half_hour():
    assert points_for_hours(0.5) == 1


def test_points_for_whole_hours():
    assert points_for_hours(1) == 1
    assert points_for_hours(3) == 3


def test_points_round_half_up():
    assert points_for_hours(1.5) == 2
    assert points_for_hours(2.5) == 3


# ---- log_hours ----

def test_log_hours():
    service, session_repo, user_repo = make_service()
    saved = new_session()
    session_repo.create_for_student.return_value = saved

    result = service.log_hours(
        student_id=7, description="Library Tutoring", hours_logged=2, session_date=YESTERDAY
    )

    session_repo.create_for_student.assert_called_once_with(
        student_id=7,
        description="Library Tutoring",
        hours_logged=2,
        session_date=YESTERDAY,
    )
    assert result is saved


def test_log_hours_trims_description():
    service, session_repo, user_repo = make_service()
    service.log_hours(
        student_id=7, description="  Tutoring  ", hours_logged=2, session_date=YESTERDAY
    )
    kwargs = session_repo.create_for_student.call_args.kwargs
    assert kwargs["description"] == "Tutoring"


def test_log_hours_empty_description():
    service, session_repo, user_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.log_hours(
            student_id=7, description="   ", hours_logged=2, session_date=YESTERDAY
        )
    session_repo.create_for_student.assert_not_called()


def test_log_hours_zero_hours():
    service, session_repo, user_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.log_hours(
            student_id=7, description="Tutoring", hours_logged=0, session_date=YESTERDAY
        )
    session_repo.create_for_student.assert_not_called()


def test_log_hours_over_24_hours():
    service, session_repo, user_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.log_hours(
            student_id=7, description="Tutoring", hours_logged=24.5, session_date=YESTERDAY
        )
    session_repo.create_for_student.assert_not_called()


def test_log_hours_future_date():
    service, session_repo, user_repo = make_service()
    tomorrow = date.today() + timedelta(days=1)
    with pytest.raises(InvalidInputError):
        service.log_hours(
            student_id=7, description="Tutoring", hours_logged=2, session_date=tomorrow
        )
    session_repo.create_for_student.assert_not_called()


# ---- approve_session ----

def test_approve_session():
    service, session_repo, user_repo = make_service()
    row = new_session(hours=2.5)
    session_repo.get_by_id.return_value = row

    service.approve_session(10)

    assert row.status == "approved"
    user_repo.add_points.assert_called_once_with(user_id=7, points=3, commit=False)
    session_repo.save.assert_called_once_with(row)


def test_approve_session_missing():
    service, session_repo, user_repo = make_service()
    session_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.approve_session(999)
    user_repo.add_points.assert_not_called()


def test_approve_session_already_approved():
    service, session_repo, user_repo = make_service()
    session_repo.get_by_id.return_value = new_session(status="approved")
    with pytest.raises(ConflictError):
        service.approve_session(10)
    user_repo.add_points.assert_not_called()
    session_repo.save.assert_not_called()


def test_approve_session_already_rejected():
    service, session_repo, user_repo = make_service()
    session_repo.get_by_id.return_value = new_session(status="rejected")
    with pytest.raises(ConflictError):
        service.approve_session(10)
    user_repo.add_points.assert_not_called()


def test_approve_session_points_fail():
    service, session_repo, user_repo = make_service()
    row = new_session()
    session_repo.get_by_id.return_value = row
    user_repo.add_points.side_effect = ValueError("User doesn't exist")
    with pytest.raises(ValueError):
        service.approve_session(10)
    assert row.status == "pending"
    session_repo.save.assert_not_called()


# ---- reject_session / review_session ----

def test_reject_session():
    service, session_repo, user_repo = make_service()
    row = new_session()
    session_repo.get_by_id.return_value = row

    service.reject_session(10)

    assert row.status == "rejected"
    user_repo.add_points.assert_not_called()
    session_repo.save.assert_called_once_with(row)


def test_reject_session_already_approved():
    service, session_repo, user_repo = make_service()
    session_repo.get_by_id.return_value = new_session(status="approved")
    with pytest.raises(ConflictError):
        service.reject_session(10)
    session_repo.save.assert_not_called()


def test_review_session_bad_decision():
    service, session_repo, user_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.review_session(10, "maybe")


# ---- viewing and listing ----

def test_student_views_own_session():
    service, session_repo, user_repo = make_service()
    row = new_session(student_id=7)
    session_repo.get_by_id.return_value = row
    assert service.get_session_for(new_user(7), 10) is row


def test_student_cannot_view_other_session():
    service, session_repo, user_repo = make_service()
    session_repo.get_by_id.return_value = new_session(student_id=7)
    with pytest.raises(PermissionDeniedError):
        service.get_session_for(new_user(8), 10)


def test_admin_views_any_session():
    service, session_repo, user_repo = make_service()
    row = new_session(student_id=7)
    session_repo.get_by_id.return_value = row
    assert service.get_session_for(new_user(1, "admin"), 10) is row


def test_list_sessions_for_admin():
    service, session_repo, user_repo = make_service()
    service.list_sessions_for(new_user(1, "admin"), "pending")
    session_repo.list_by_status.assert_called_once_with("pending")
    session_repo.list_for_student.assert_not_called()


def test_list_sessions_for_student():
    service, session_repo, user_repo = make_service()
    session_repo.list_for_student.return_value = [
        new_session(status="pending"),
        new_session(status="approved"),
    ]
    result = service.list_sessions_for(new_user(7), "approved")
    session_repo.list_for_student.assert_called_once_with(7)
    assert len(result) == 1
    assert result[0].status == "approved"


def test_list_sessions_bad_status():
    service, session_repo, user_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.list_sessions_for(new_user(7), "denied")
