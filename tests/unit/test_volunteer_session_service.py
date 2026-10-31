"""Unit tests: VolunteerSessionService with mocked repositories (no database)."""

import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock

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


class PointsUnitTests(unittest.TestCase):

    def test_points_for_half_hour(self):
        self.assertEqual(points_for_hours(0.5), 1)

    def test_points_for_whole_hours(self):
        self.assertEqual(points_for_hours(1), 1)
        self.assertEqual(points_for_hours(3), 3)

    def test_points_round_half_up(self):
        self.assertEqual(points_for_hours(1.5), 2)
        self.assertEqual(points_for_hours(2.5), 3)


class VolunteerSessionServiceUnitTests(unittest.TestCase):

    def setUp(self):
        self.service, self.session_repo, self.user_repo = make_service()

    # ---- log_hours ----

    def test_log_hours(self):
        saved = new_session()
        self.session_repo.create_for_student.return_value = saved

        result = self.service.log_hours(
            student_id=7, description="Library Tutoring", hours_logged=2, session_date=YESTERDAY
        )

        self.session_repo.create_for_student.assert_called_once_with(
            student_id=7,
            description="Library Tutoring",
            hours_logged=2,
            session_date=YESTERDAY,
        )
        self.assertIs(result, saved)

    def test_log_hours_trims_description(self):
        self.service.log_hours(
            student_id=7, description="  Tutoring  ", hours_logged=2, session_date=YESTERDAY
        )
        kwargs = self.session_repo.create_for_student.call_args.kwargs
        self.assertEqual(kwargs["description"], "Tutoring")

    def test_log_hours_empty_description(self):
        with self.assertRaises(InvalidInputError):
            self.service.log_hours(
                student_id=7, description="   ", hours_logged=2, session_date=YESTERDAY
            )
        self.session_repo.create_for_student.assert_not_called()

    def test_log_hours_zero_hours(self):
        with self.assertRaises(InvalidInputError):
            self.service.log_hours(
                student_id=7, description="Tutoring", hours_logged=0, session_date=YESTERDAY
            )
        self.session_repo.create_for_student.assert_not_called()

    def test_log_hours_over_24_hours(self):
        with self.assertRaises(InvalidInputError):
            self.service.log_hours(
                student_id=7, description="Tutoring", hours_logged=24.5, session_date=YESTERDAY
            )
        self.session_repo.create_for_student.assert_not_called()

    def test_log_hours_future_date(self):
        tomorrow = date.today() + timedelta(days=1)
        with self.assertRaises(InvalidInputError):
            self.service.log_hours(
                student_id=7, description="Tutoring", hours_logged=2, session_date=tomorrow
            )
        self.session_repo.create_for_student.assert_not_called()

    # ---- approve_session ----

    def test_approve_session(self):
        row = new_session(hours=2.5)
        self.session_repo.get_by_id.return_value = row

        self.service.approve_session(10)

        self.assertEqual(row.status, "approved")
        self.user_repo.add_points.assert_called_once_with(user_id=7, points=3, commit=False)
        self.session_repo.save.assert_called_once_with(row)

    def test_approve_session_missing(self):
        self.session_repo.get_by_id.return_value = None
        with self.assertRaises(NotFoundError):
            self.service.approve_session(999)
        self.user_repo.add_points.assert_not_called()

    def test_approve_session_already_approved(self):
        self.session_repo.get_by_id.return_value = new_session(status="approved")
        with self.assertRaises(ConflictError):
            self.service.approve_session(10)
        self.user_repo.add_points.assert_not_called()
        self.session_repo.save.assert_not_called()

    def test_approve_session_already_rejected(self):
        self.session_repo.get_by_id.return_value = new_session(status="rejected")
        with self.assertRaises(ConflictError):
            self.service.approve_session(10)
        self.user_repo.add_points.assert_not_called()

    def test_approve_session_points_fail(self):
        row = new_session()
        self.session_repo.get_by_id.return_value = row
        self.user_repo.add_points.side_effect = ValueError("User doesn't exist")
        with self.assertRaises(ValueError):
            self.service.approve_session(10)
        self.assertEqual(row.status, "pending")
        self.session_repo.save.assert_not_called()

    # ---- reject_session / review_session ----

    def test_reject_session(self):
        row = new_session()
        self.session_repo.get_by_id.return_value = row

        self.service.reject_session(10)

        self.assertEqual(row.status, "rejected")
        self.user_repo.add_points.assert_not_called()
        self.session_repo.save.assert_called_once_with(row)

    def test_reject_session_already_approved(self):
        self.session_repo.get_by_id.return_value = new_session(status="approved")
        with self.assertRaises(ConflictError):
            self.service.reject_session(10)
        self.session_repo.save.assert_not_called()

    def test_review_session_bad_decision(self):
        with self.assertRaises(InvalidInputError):
            self.service.review_session(10, "maybe")

    # ---- viewing and listing ----

    def test_student_views_own_session(self):
        row = new_session(student_id=7)
        self.session_repo.get_by_id.return_value = row
        self.assertIs(self.service.get_session_for(new_user(7), 10), row)

    def test_student_cannot_view_other_session(self):
        self.session_repo.get_by_id.return_value = new_session(student_id=7)
        with self.assertRaises(PermissionDeniedError):
            self.service.get_session_for(new_user(8), 10)

    def test_admin_views_any_session(self):
        row = new_session(student_id=7)
        self.session_repo.get_by_id.return_value = row
        self.assertIs(self.service.get_session_for(new_user(1, "admin"), 10), row)

    def test_list_sessions_for_admin(self):
        self.service.list_sessions_for(new_user(1, "admin"), "pending")
        self.session_repo.list_by_status.assert_called_once_with("pending")
        self.session_repo.list_for_student.assert_not_called()

    def test_list_sessions_for_student(self):
        self.session_repo.list_for_student.return_value = [
            new_session(status="pending"),
            new_session(status="approved"),
        ]
        result = self.service.list_sessions_for(new_user(7), "approved")
        self.session_repo.list_for_student.assert_called_once_with(7)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, "approved")

    def test_list_sessions_bad_status(self):
        with self.assertRaises(InvalidInputError):
            self.service.list_sessions_for(new_user(7), "denied")
