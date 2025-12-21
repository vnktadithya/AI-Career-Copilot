from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.core.security import verify_supabase_jwt, AuthError
from backend.app.api.v1.dependencies import get_current_user
from backend.app.models.user import CurrentUser
from backend.app.models.session import SessionResponse

router = APIRouter(prefix="/auth")
security = HTTPBearer(auto_error=True)
    

@router.get("/me", response_model=CurrentUser)
def whoami(current_user: CurrentUser = Depends(get_current_user)):
    return current_user


@router.get("/session", response_model=SessionResponse)
def get_session(current_user: CurrentUser = Depends(get_current_user)):
    return SessionResponse(
        user_id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_new_user=False,  # will evolve later
    )

