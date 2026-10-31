"""Unit tests: the data models and their default values."""

import unittest
from datetime import date

from app.models.award import Award
from app.models.redemption_claim import RedemptionClaim
from app.models.user import User
from app.models.volunteer_session import VolunteerSession


class ModelUnitTests(unittest.TestCase):

    def test_new_user(self):
        user = User(username="bob", email="bob@example.com", password="bobpass")
        self.assertEqual(user.username, "bob")
        self.assertEqual(user.total_points, 0)

    def test_new_volunteer_session(self):
        session = VolunteerSession(
            student_id=1, description="Beach Cleanup", hours_logged=3, date=date.today()
        )
        self.assertEqual(session.description, "Beach Cleanup")
        self.assertEqual(session.status, "pending")

    def test_new_award(self):
        award = Award(name="Hoodie", description="Warm", points_required=100, stock_quantity=3)
        self.assertEqual(award.name, "Hoodie")
        self.assertEqual(award.points_required, 100)
        self.assertEqual(award.stock_quantity, 3)

    def test_new_redemption_claim(self):
        claim = RedemptionClaim(student_id=1, award_id=2)
        self.assertEqual(claim.status, "submitted")
        self.assertEqual(claim.claim_date, date.today())
