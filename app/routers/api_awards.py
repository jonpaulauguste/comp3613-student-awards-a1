from fastapi import Response, status

from app.dependencies import AdminDep, AuthDep, SessionDep
from app.dependencies.auth import StudentDep
from app.repositories.award import AwardRepository
from app.repositories.redemption_claim import RedemptionClaimRepository
from app.repositories.user import UserRepository
from app.schemas.api import (
    AwardCreate,
    AwardResponse,
    AwardUpdate,
    RedemptionCreate,
    RedemptionResponse,
)
from app.services.award_service import AwardService
from app.services.reward_redemption_service import RewardRedemptionService
from . import api_router


def _redemptions(db) -> RewardRedemptionService:
    return RewardRedemptionService(
        UserRepository(db), AwardRepository(db), RedemptionClaimRepository(db)
    )


@api_router.get("/awards", response_model=list[AwardResponse])
async def api_list_awards(user: AuthDep, db: SessionDep):
    return AwardService(AwardRepository(db)).list_awards()


@api_router.get("/awards/{award_id}", response_model=AwardResponse)
async def api_get_award(award_id: int, user: AuthDep, db: SessionDep):
    return AwardService(AwardRepository(db)).get_award(award_id)


@api_router.post(
    "/awards", response_model=AwardResponse, status_code=status.HTTP_201_CREATED
)
async def api_create_award(payload: AwardCreate, admin: AdminDep, db: SessionDep):
    return AwardService(AwardRepository(db)).create_award(**payload.model_dump())


@api_router.patch("/awards/{award_id}", response_model=AwardResponse)
async def api_update_award(
    award_id: int, payload: AwardUpdate, admin: AdminDep, db: SessionDep
):
    return AwardService(AwardRepository(db)).update_award(
        award_id, **payload.model_dump(exclude_unset=True)
    )


@api_router.delete("/awards/{award_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_award(award_id: int, admin: AdminDep, db: SessionDep):
    AwardService(AwardRepository(db)).delete_award(award_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api_router.get("/redemptions", response_model=list[RedemptionResponse])
async def api_list_redemptions(user: AuthDep, db: SessionDep):
    """Students get their own claims; admins get every claim."""
    return _redemptions(db).list_claims_for(user)


@api_router.post(
    "/redemptions",
    response_model=RedemptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def api_redeem_award(payload: RedemptionCreate, student: StudentDep, db: SessionDep):
    return _redemptions(db).redeem_award(student_id=student.id, award_id=payload.award_id)
