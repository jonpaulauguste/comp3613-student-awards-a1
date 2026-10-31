"""Unit tests: AwardService (admin award catalogue) with a mocked repository."""

from unittest.mock import MagicMock

import pytest

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


def test_create_award():
    service, award_repo = make_service()
    award = service.create_award(
        name="  Hoodie ", description=" Warm ", points_required=100, stock_quantity=3
    )
    award_repo.save.assert_called_once()
    assert award.name == "Hoodie"
    assert award.description == "Warm"
    assert award.points_required == 100
    assert award.stock_quantity == 3


def test_create_award_blank_name():
    service, award_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.create_award(
            name="   ", description="", points_required=10, stock_quantity=1
        )
    award_repo.save.assert_not_called()


def test_create_award_zero_points():
    service, award_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.create_award(
            name="Hoodie", description="", points_required=0, stock_quantity=1
        )
    award_repo.save.assert_not_called()


def test_create_award_negative_stock():
    service, award_repo = make_service()
    with pytest.raises(InvalidInputError):
        service.create_award(
            name="Hoodie", description="", points_required=10, stock_quantity=-1
        )
    award_repo.save.assert_not_called()


def test_update_award():
    service, award_repo = make_service()
    award_repo.get_by_id.return_value = hoodie()
    award = service.update_award(4, stock_quantity=10)
    assert award.stock_quantity == 10
    assert award.name == "Hoodie"
    assert award.points_required == 100


def test_update_award_missing():
    service, award_repo = make_service()
    award_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.update_award(99, name="Hoodie")


def test_delete_award():
    service, award_repo = make_service()
    award = hoodie()
    award_repo.get_by_id.return_value = award
    award_repo.count_claims.return_value = 0
    service.delete_award(4)
    award_repo.delete.assert_called_once_with(award)


def test_delete_award_with_claims():
    service, award_repo = make_service()
    award_repo.get_by_id.return_value = hoodie()
    award_repo.count_claims.return_value = 2
    with pytest.raises(ConflictError):
        service.delete_award(4)
    award_repo.delete.assert_not_called()
