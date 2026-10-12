from app.models.redemption_claim import RedemptionClaim
from app.repositories.award import AwardRepository
from app.repositories.redemption_claim import RedemptionClaimRepository
from app.repositories.user import UserRepository


class RewardRedemptionService:
    def __init__(
        self,
        user_repository: UserRepository,
        award_repository: AwardRepository,
        redemption_claim_repository: RedemptionClaimRepository,
    ):
        self.user_repository = user_repository
        self.award_repository = award_repository
        self.redemption_claim_repository = redemption_claim_repository

    def _eligibility_reason(self, current_points: int, points_required: int, stock_quantity: int) -> str:
        if stock_quantity <= 0:
            return "Out of stock."
        if current_points < points_required:
            missing = points_required - current_points
            return f"You need {missing} more point(s)."
        return ""

    def list_catalog_for_student(self, student_id: int) -> list[dict]:
        student = self.user_repository.get_by_id(student_id)
        if not student:
            raise ValueError("Student account was not found.")

        awards = self.award_repository.list_all()
        catalog: list[dict] = []
        for award in awards:
            reason = self._eligibility_reason(
                current_points=student.total_points,
                points_required=award.points_required,
                stock_quantity=award.stock_quantity,
            )
            catalog.append(
                {
                    "award": award,
                    "eligible": reason == "",
                    "ineligible_reason": reason,
                }
            )
        return catalog

    def redeem_award(self, student_id: int, award_id: int) -> RedemptionClaim:
        student = self.user_repository.get_by_id(student_id)
        if not student:
            raise ValueError("Student account was not found.")

        award = self.award_repository.get_by_id(award_id)
        if not award:
            raise ValueError("Award was not found.")

        reason = self._eligibility_reason(
            current_points=student.total_points,
            points_required=award.points_required,
            stock_quantity=award.stock_quantity,
        )
        if reason:
            raise ValueError(reason)

        self.user_repository.deduct_points(student.id, award.points_required)
        award.stock_quantity -= 1
        self.award_repository.save(award)
        return self.redemption_claim_repository.create(
            RedemptionClaim(
                student_id=student.id,
                award_id=award.id,
                status="submitted",
            )
        )
