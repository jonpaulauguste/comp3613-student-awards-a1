from datetime import date

from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.award import AwardRepository
from app.repositories.redemption_claim import RedemptionClaimRepository
from app.repositories.user import UserRepository
from app.repositories.volunteer_session import VolunteerSessionRepository
from app.services.reward_redemption_service import RewardRedemptionService
from app.services.volunteer_session_service import VolunteerSessionService
from app.utilities.flash import flash
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    if user.role == "admin":
        return RedirectResponse(
            url=request.url_for("admin_home_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    volunteer_repo = VolunteerSessionRepository(db)
    user_repo = UserRepository(db)
    volunteer_service = VolunteerSessionService(volunteer_repo, user_repo)
    volunteer_sessions = volunteer_service.get_student_sessions(user.id)

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "volunteer_sessions": volunteer_sessions,
        },
    )


@router.post("/app/volunteer-sessions", response_class=HTMLResponse)
async def log_volunteer_hours_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    description: str = Form(),
    hours_logged: float = Form(),
    session_date: date = Form(),
):
    volunteer_repo = VolunteerSessionRepository(db)
    user_repo = UserRepository(db)
    volunteer_service = VolunteerSessionService(volunteer_repo, user_repo)
    try:
        volunteer_service.log_hours(
            student_id=user.id,
            description=description,
            hours_logged=hours_logged,
            session_date=session_date,
        )
        flash(request, "Volunteer hours submitted for approval.")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    except Exception:
        flash(request, "Unable to submit volunteer hours right now.", "danger")

    return RedirectResponse(
        url=request.url_for("user_home_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/app/rewards", response_class=HTMLResponse)
async def rewards_catalogue_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    user_repo = UserRepository(db)
    award_repo = AwardRepository(db)
    claim_repo = RedemptionClaimRepository(db)
    reward_service = RewardRedemptionService(user_repo, award_repo, claim_repo)
    award_name_lookup = {award.id: award.name for award in award_repo.list_all() if award.id is not None}

    return templates.TemplateResponse(
        request=request,
        name="rewards.html",
        context={
            "user": user,
            "award_catalogue": reward_service.list_catalog_for_student(user.id),
            "redemption_claims": claim_repo.list_for_student(user.id),
            "award_name_lookup": award_name_lookup,
        },
    )


@router.post("/app/rewards/{award_id}/redeem", response_class=HTMLResponse)
async def redeem_award_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    award_id: int,
):
    user_repo = UserRepository(db)
    award_repo = AwardRepository(db)
    claim_repo = RedemptionClaimRepository(db)
    reward_service = RewardRedemptionService(user_repo, award_repo, claim_repo)
    try:
        reward_service.redeem_award(student_id=user.id, award_id=award_id)
        flash(request, "Your redemption request was submitted.")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    except Exception:
        flash(request, "Unable to process this redemption right now.", "danger")

    return RedirectResponse(
        url=request.url_for("rewards_catalogue_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )