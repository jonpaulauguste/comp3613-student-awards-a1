"""Unit tests: AwardService (admin award catalogue) with a mocked repository."""

import unittest
from unittest.mock import MagicMock

from app.models.award import Award
from app.services.award_service import AwardService
from app.services.errors import ConflictError, InvalidInputError, NotFoundError


def make_service():
    award_repo = MagicMock()
    award_repo.save.side_effect = lambda award: award
    return AwardService(award_repo), award_repo


def hoodie():
    return Award(
        id=4,
        name="Hoodie",
        description="University hoodie",
        points_required=100,
        stock_quantity=3,
    )


class AwardServiceUnitTests(unittest.TestCase):

    def setUp(self):
        self.service, self.award_repo = make_service()

    def test_create_award(self):
        award = self.service.create_award(
            name="  Hoodie ", description=" Warm ", points_required=100, stock_quantity=3
        )
        self.award_repo.save.assert_called_once()
        self.assertEqual(award.name, "Hoodie")
        self.assertEqual(award.description, "Warm")
        self.assertEqual(award.points_required, 100)
        self.assertEqual(award.stock_quantity, 3)

    def test_create_award_blank_name(self):
        with self.assertRaises(InvalidInputError):
            self.service.create_award(
                name="   ", description="", points_required=10, stock_quantity=1
            )
        self.award_repo.save.assert_not_called()

    def test_create_award_zero_points(self):
        with self.assertRaises(InvalidInputError):
            self.service.create_award(
                name="Hoodie", description="", points_required=0, stock_quantity=1
            )
        self.award_repo.save.assert_not_called()

    def test_create_award_negative_stock(self):
        with self.assertRaises(InvalidInputError):
            self.service.create_award(
                name="Hoodie", description="", points_required=10, stock_quantity=-1
            )
        self.award_repo.save.assert_not_called()

    def test_update_award(self):
        self.award_repo.get_by_id.return_value = hoodie()
        award = self.service.update_award(4, stock_quantity=10)
        self.assertEqual(award.stock_quantity, 10)
        self.assertEqual(award.name, "Hoodie")
        self.assertEqual(award.points_required, 100)

    def test_update_award_missing(self):
        self.award_repo.get_by_id.return_value = None
        with self.assertRaises(NotFoundError):
            self.service.update_award(99, name="Hoodie")

    def test_delete_award(self):
        award = hoodie()
        self.award_repo.get_by_id.return_value = award
        self.award_repo.count_claims.return_value = 0
        self.service.delete_award(4)
        self.award_repo.delete.assert_called_once_with(award)

    def test_delete_award_with_claims(self):
        self.award_repo.get_by_id.return_value = hoodie()
        self.award_repo.count_claims.return_value = 2
        with self.assertRaises(ConflictError):
            self.service.delete_award(4)
        self.award_repo.delete.assert_not_called()
