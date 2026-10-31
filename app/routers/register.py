from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form, HTTPException
from app.dependencies import SessionDep
from app.schemas.auth import SignupRequest
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from . import router, templates

# View route (loads the page)
@router.get("/register", response_class=HTMLResponse)
async def register_view(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="register.html",
    )

# Action route (performs an action)
@router.post('/register', response_class=HTMLResponse)
def signup_user(request:Request, db:SessionDep, 
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    try:
        user = auth_service.register_user(username, email, password)
        flash(request, "Registration completed! Sign in now!")
        return RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
    except ValueError as e:
        # Covers duplicate username/email (ConflictError), short password and bad email.
        message = str(e) if not hasattr(e, "errors") else "Please enter a valid email address."
        flash(request, message, "danger")
        return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)
    except Exception:
        flash(request, "Registration failed. Please try again.", "danger")
        return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)
