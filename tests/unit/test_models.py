"""Unit tests: the data models and their default values."""

from datetime import date

from app.models.award import Award
from app.models.redemption_claim import RedemptionClaim
from app.models.user import User
from app.models.volunteer_session import VolunteerSession


def test_new_user():
    user = User(username="bob", email="bob@example.com", password="bobpass")
    assert user.username == "bob"
    assert user.total_points == 0


def test_new_volunteer_session():
    session = VolunteerSession(
        student_id=1, description="Beach Cleanup", hours_logged=3, date=date.today()
    )
    assert session.description == "Beach Cleanup"
    assert session.status == "pending"


def test_new_award():
    award = Award(name="Hoodie", description="Warm", points_required=100, stock_quantity=3)
    assert award.name == "Hoodie"
    assert award.points_required == 100
    assert award.stock_quantity == 3


def test_new_redemption_claim():
    claim = RedemptionClaim(student_id=1, award_id=2)
    assert claim.status == "submitted"
    assert claim.claim_date == date.today()
