from fastapi import Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AdminDep
from app.dependencies.session import SessionDep
from app.repositories.user import UserRepository
from app.repositories.volunteer_session import VolunteerSessionRepository
from app.services.volunteer_session_service import VolunteerSessionService
from app.utilities.flash import flash
from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    volunteer_repo = VolunteerSessionRepository(db)
    user_repo = UserRepository(db)
    volunteer_service = VolunteerSessionService(volunteer_repo, user_repo)
    pending_sessions = volunteer_service.get_pending_sessions()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": user,
            "pending_sessions": pending_sessions,
        },
    )


@router.post("/admin/volunteer-sessions/{session_id}/approve", response_class=HTMLResponse)
async def approve_volunteer_hours_action(
    session_id: int,
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    volunteer_repo = VolunteerSessionRepository(db)
    user_repo = UserRepository(db)
    volunteer_service = VolunteerSessionService(volunteer_repo, user_repo)
    try:
        volunteer_service.approve_session(volunteer_session_id=session_id)
        flash(request, "Volunteer session approved and points awarded.")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    except Exception:
        flash(request, "Unable to approve volunteer session right now.", "danger")

    return RedirectResponse(
        url=request.url_for("admin_home_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
