"""Unit tests: RewardRedemptionService with mocked repositories (no database)."""

import unittest
from unittest.mock import MagicMock

from app.models.award import Award
from app.models.user import User
from app.services.errors import ConflictError, InvalidInputError, NotFoundError
from app.services.reward_redemption_service import RewardRedemptionService


def make_service():
    user_repo = MagicMock()
    award_repo = MagicMock()
    claim_repo = MagicMock()
    claim_repo.create.side_effect = lambda claim: claim
    service = RewardRedemptionService(user_repo, award_repo, claim_repo)
    return service, user_repo, award_repo, claim_repo


def new_student(points=100, role="regular_user"):
    return User(
        id=7,
        username="bob",
        email="bob@example.com",
        password="x",
        role=role,
        total_points=points,
    )


def new_award(points_required=40, stock=5, award_id=3):
    return Award(
        id=award_id,
        name="Study Pack",
        description="Notebook and pens",
        points_required=points_required,
        stock_quantity=stock,
    )


class RewardRedemptionServiceUnitTests(unittest.TestCase):

    def setUp(self):
        self.service, self.user_repo, self.award_repo, self.claim_repo = make_service()

    def test_redeem_award(self):
        self.user_repo.get_by_id.return_value = new_student(points=100)
        award = new_award(points_required=40, stock=5)
        self.award_repo.get_by_id.return_value = award

        claim = self.service.redeem_award(student_id=7, award_id=3)

        self.user_repo.deduct_points.assert_called_once_with(7, 40, commit=False)
        self.assertEqual(award.stock_quantity, 4)
        self.award_repo.save.assert_called_once_with(award, commit=False)
        self.assertEqual(claim.student_id, 7)
        self.assertEqual(claim.award_id, 3)
        self.assertEqual(claim.status, "submitted")

    def test_redeem_award_exact_points(self):
        self.user_repo.get_by_id.return_value = new_student(points=40)
        self.award_repo.get_by_id.return_value = new_award(points_required=40)
        self.service.redeem_award(student_id=7, award_id=3)
        self.user_repo.deduct_points.assert_called_once()

    def test_redeem_award_not_enough_points(self):
        self.user_repo.get_by_id.return_value = new_student(points=10)
        award = new_award(points_required=40, stock=5)
        self.award_repo.get_by_id.return_value = award

        with self.assertRaises(InvalidInputError) as error:
            self.service.redeem_award(student_id=7, award_id=3)

        self.assertIn("30 more point", str(error.exception))
        self.user_repo.deduct_points.assert_not_called()
        self.claim_repo.create.assert_not_called()
        self.assertEqual(award.stock_quantity, 5)

    def test_redeem_award_out_of_stock(self):
        self.user_repo.get_by_id.return_value = new_student(points=500)
        self.award_repo.get_by_id.return_value = new_award(stock=0)
        with self.assertRaises(ConflictError):
            self.service.redeem_award(student_id=7, award_id=3)
        self.claim_repo.create.assert_not_called()

    def test_redeem_award_missing_award(self):
        self.user_repo.get_by_id.return_value = new_student()
        self.award_repo.get_by_id.return_value = None
        with self.assertRaises(NotFoundError):
            self.service.redeem_award(student_id=7, award_id=99)

    def test_redeem_award_missing_student(self):
        self.user_repo.get_by_id.return_value = None
        with self.assertRaises(NotFoundError):
            self.service.redeem_award(student_id=99, award_id=3)

    def test_catalog_eligibility(self):
        self.user_repo.get_by_id.return_value = new_student(points=50)
        self.award_repo.list_all.return_value = [
            new_award(points_required=15, award_id=1),
            new_award(points_required=60, award_id=2),
            new_award(points_required=10, stock=0, award_id=3),
        ]

        catalog = self.service.list_catalog_for_student(7)

        self.assertTrue(catalog[0]["eligible"])
        self.assertFalse(catalog[1]["eligible"])
        self.assertEqual(catalog[1]["ineligible_reason"], "You need 10 more point(s).")
        self.assertFalse(catalog[2]["eligible"])
        self.assertEqual(catalog[2]["ineligible_reason"], "Out of stock.")

    def test_list_claims_for_student(self):
        self.service.list_claims_for(new_student())
        self.claim_repo.list_for_student.assert_called_once_with(7)
        self.claim_repo.list_all.assert_not_called()

    def test_list_claims_for_admin(self):
        self.service.list_claims_for(new_student(role="admin"))
        self.claim_repo.list_all.assert_called_once()
        self.claim_repo.list_for_student.assert_not_called()
