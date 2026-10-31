from typing import Optional

from app.models.award import Award
from app.repositories.award import AwardRepository
from app.services.errors import ConflictError, InvalidInputError, NotFoundError


class AwardService:
    """Admin management of the award catalogue."""

    def __init__(self, award_repository: AwardRepository):
        self.award_repository = award_repository

    def list_awards(self) -> list[Award]:
        return self.award_repository.list_all()

    def get_award(self, award_id: int) -> Award:
        award = self.award_repository.get_by_id(award_id)
        if award is None:
            raise NotFoundError("Award was not found.")
        return award

    def create_award(
        self,
        *,
        name: str,
        description: str,
        points_required: int,
        stock_quantity: int,
    ) -> Award:
        award = Award(
            name=self._clean_name(name),
            description=(description or "").strip(),
            points_required=self._check_points(points_required),
            stock_quantity=self._check_stock(stock_quantity),
        )
        return self.award_repository.save(award)

    def update_award(
        self,
        award_id: int,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        points_required: Optional[int] = None,
        stock_quantity: Optional[int] = None,
    ) -> Award:
        award = self.get_award(award_id)
        if name is not None:
            award.name = self._clean_name(name)
        if description is not None:
            award.description = description.strip()
        if points_required is not None:
            award.points_required = self._check_points(points_required)
        if stock_quantity is not None:
            award.stock_quantity = self._check_stock(stock_quantity)
        return self.award_repository.save(award)

    def delete_award(self, award_id: int) -> None:
        award = self.get_award(award_id)
        if self.award_repository.count_claims(award_id) > 0:
            raise ConflictError(
                "This award has redemption claims and cannot be deleted. Set its stock to 0 instead."
            )
        self.award_repository.delete(award)

    @staticmethod
    def _clean_name(name: str) -> str:
        cleaned = (name or "").strip()
        if not cleaned:
            raise InvalidInputError("Award name is required.")
        if len(cleaned) > 120:
            raise InvalidInputError("Award name must be 120 characters or fewer.")
        return cleaned

    @staticmethod
    def _check_points(points_required: int) -> int:
        if points_required is None or points_required < 1:
            raise InvalidInputError("Points required must be at least 1.")
        return points_required

    @staticmethod
    def _check_stock(stock_quantity: int) -> int:
        if stock_quantity is None or stock_quantity < 0:
            raise InvalidInputError("Stock quantity cannot be negative.")
        return stock_quantity
