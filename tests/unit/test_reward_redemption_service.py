"""Unit tests: RewardRedemptionService with mocked repositories (no database)."""

from unittest.mock import MagicMock

import pytest

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


def test_redeem_award():
    service, user_repo, award_repo, claim_repo = make_service()
    user_repo.get_by_id.return_value = new_student(points=100)
    award = new_award(points_required=40, stock=5)
    award_repo.get_by_id.return_value = award

    claim = service.redeem_award(student_id=7, award_id=3)

    user_repo.deduct_points.assert_called_once_with(7, 40, commit=False)
    assert award.stock_quantity == 4
    award_repo.save.assert_called_once_with(award, commit=False)
    assert claim.student_id == 7
    assert claim.award_id == 3
    assert claim.status == "submitted"


def test_redeem_award_exact_points():
    service, user_repo, award_repo, claim_repo = make_service()
    user_repo.get_by_id.return_value = new_student(points=40)
    award_repo.get_by_id.return_value = new_award(points_required=40)
    service.redeem_award(student_id=7, award_id=3)
    user_repo.deduct_points.assert_called_once()


def test_redeem_award_not_enough_points():
    service, user_repo, award_repo, claim_repo = make_service()
    user_repo.get_by_id.return_value = new_student(points=10)
    award = new_award(points_required=40, stock=5)
    award_repo.get_by_id.return_value = award

    with pytest.raises(InvalidInputError) as error:
        service.redeem_award(student_id=7, award_id=3)

    assert "30 more point" in str(error.value)
    user_repo.deduct_points.assert_not_called()
    claim_repo.create.assert_not_called()
    assert award.stock_quantity == 5


def test_redeem_award_out_of_stock():
    service, user_repo, award_repo, claim_repo = make_service()
    user_repo.get_by_id.return_value = new_student(points=500)
    award_repo.get_by_id.return_value = new_award(stock=0)
    with pytest.raises(ConflictError):
        service.redeem_award(student_id=7, award_id=3)
    claim_repo.create.assert_not_called()


def test_redeem_award_missing_award():
    service, user_repo, award_repo, claim_repo = make_service()
    user_repo.get_by_id.return_value = new_student()
    award_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.redeem_award(student_id=7, award_id=99)


def test_redeem_award_missing_student():
    service, user_repo, award_repo, claim_repo = make_service()
    user_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        service.redeem_award(student_id=99, award_id=3)


def test_catalog_eligibility():
    service, user_repo, award_repo, claim_repo = make_service()
    user_repo.get_by_id.return_value = new_student(points=50)
    award_repo.list_all.return_value = [
        new_award(points_required=15, award_id=1),
        new_award(points_required=60, award_id=2),
        new_award(points_required=10, stock=0, award_id=3),
    ]

    catalog = service.list_catalog_for_student(7)

    assert catalog[0]["eligible"] is True
    assert catalog[1]["eligible"] is False
    assert catalog[1]["ineligible_reason"] == "You need 10 more point(s)."
    assert catalog[2]["eligible"] is False
    assert catalog[2]["ineligible_reason"] == "Out of stock."


def test_list_claims_for_student():
    service, user_repo, award_repo, claim_repo = make_service()
    service.list_claims_for(new_student())
    claim_repo.list_for_student.assert_called_once_with(7)
    claim_repo.list_all.assert_not_called()


def test_list_claims_for_admin():
    service, user_repo, award_repo, claim_repo = make_service()
    service.list_claims_for(new_student(role="admin"))
    claim_repo.list_all.assert_called_once()
    claim_repo.list_for_student.assert_not_called()
