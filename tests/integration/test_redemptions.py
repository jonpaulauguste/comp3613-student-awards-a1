"""Integration tests: redeeming awards and managing the catalogue (real database)."""

from datetime import date, timedelta

import pytest

from app.repositories.award import AwardRepository
from app.repositories.redemption_claim import RedemptionClaimRepository
from app.repositories.user import UserRepository
from app.repositories.volunteer_session import VolunteerSessionRepository
from app.services.award_service import AwardService
from app.services.errors import ConflictError, InvalidInputError, NotFoundError
from app.services.reward_redemption_service import RewardRedemptionService
from app.services.volunteer_session_service import VolunteerSessionService
from tests.conftest import make_award, make_session, make_user


def redemption_service(db):
    return RewardRedemptionService(
        UserRepository(db), AwardRepository(db), RedemptionClaimRepository(db)
    )


def award_service(db):
    return AwardService(AwardRepository(db))


def test_redeem_award(db):
    student = make_user(db, points=20)
    award = make_award(db, points_required=15, stock_quantity=4)

    claim = redemption_service(db).redeem_award(student.id, award.id)

    db.refresh(student)
    db.refresh(award)
    assert claim.id is not None
    assert claim.status == "submitted"
    assert claim.student_id == student.id
    assert claim.award_id == award.id
    assert student.total_points == 5
    assert award.stock_quantity == 3
    assert len(RedemptionClaimRepository(db).list_for_student(student.id)) == 1


def test_redeem_award_not_enough_points(db):
    student = make_user(db, points=10)
    award = make_award(db, points_required=50, stock_quantity=3)

    with pytest.raises(InvalidInputError):
        redemption_service(db).redeem_award(student.id, award.id)

    db.refresh(student)
    db.refresh(award)
    assert student.total_points == 10
    assert award.stock_quantity == 3
    assert RedemptionClaimRepository(db).list_for_student(student.id) == []


def test_redeem_award_out_of_stock(db):
    student = make_user(db, points=500)
    award = make_award(db, points_required=10, stock_quantity=0)

    with pytest.raises(ConflictError):
        redemption_service(db).redeem_award(student.id, award.id)

    db.refresh(student)
    assert student.total_points == 500


def test_redeem_last_item_twice(db):
    student = make_user(db, points=500)
    award = make_award(db, points_required=10, stock_quantity=1)
    service = redemption_service(db)
    service.redeem_award(student.id, award.id)

    with pytest.raises(ConflictError):
        service.redeem_award(student.id, award.id)

    db.refresh(student)
    assert student.total_points == 490


def test_redeem_missing_award(db, student):
    with pytest.raises(NotFoundError):
        redemption_service(db).redeem_award(student.id, 999)


def test_pending_hours_do_not_count(db, student):
    make_session(db, student, hours=20, status="pending")
    award = make_award(db, points_required=10)

    with pytest.raises(InvalidInputError):
        redemption_service(db).redeem_award(student.id, award.id)


def test_log_approve_and_redeem(db, student):
    award = make_award(db, points_required=5, stock_quantity=2)
    volunteer_service = VolunteerSessionService(
        VolunteerSessionRepository(db), UserRepository(db)
    )

    logged = volunteer_service.log_hours(
        student_id=student.id,
        description="Career Fair",
        hours_logged=6,
        session_date=date.today() - timedelta(days=1),
    )
    volunteer_service.approve_session(logged.id)
    redemption_service(db).redeem_award(student.id, award.id)

    db.refresh(student)
    db.refresh(award)
    assert student.total_points == 1
    assert award.stock_quantity == 1


def test_create_and_update_award(db):
    service = award_service(db)

    award = service.create_award(
        name="University Hoodie", description="Warm", points_required=100, stock_quantity=3
    )
    service.update_award(award.id, stock_quantity=7)

    found = service.get_award(award.id)
    assert found.name == "University Hoodie"
    assert found.stock_quantity == 7


def test_list_awards_cheapest_first(db):
    make_award(db, "Gift Card", points_required=100)
    make_award(db, "Coffee", points_required=15)

    names = [award.name for award in award_service(db).list_awards()]

    assert names == ["Coffee", "Gift Card"]


def test_delete_award(db):
    award = make_award(db)
    service = award_service(db)
    service.delete_award(award.id)
    with pytest.raises(NotFoundError):
        service.get_award(award.id)


def test_delete_award_with_claims(db):
    student = make_user(db, points=50)
    award = make_award(db, points_required=10, stock_quantity=2)
    redemption_service(db).redeem_award(student.id, award.id)

    with pytest.raises(ConflictError):
        award_service(db).delete_award(award.id)

    assert award_service(db).get_award(award.id).id == award.id
