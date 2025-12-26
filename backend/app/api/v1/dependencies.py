from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.core.security import verify_supabase_jwt, AuthError
from backend.app.models.user import CurrentUser
from backend.app.services.user_service import get_user_by_id, create_user
import jwt
from backend.app.core.config import get_settings
from supabase import create_client, Client
import logging
logger = logging.getLogger(__name__)

settings = get_settings()
security = HTTPBearer(auto_error=True)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),) -> CurrentUser:
    try:
        token = credentials.credentials
        payload = verify_supabase_jwt(token)

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role") or payload.get("app_metadata", {}).get("role", "user")

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        # 🔑 Ensure application user exists
        user = get_user_by_id(user_id)

        if not user:
            user = create_user(
                user_id=user_id,
                email=email,
                role=role,
            )

        return CurrentUser(
            id=user["id"],
            email=user["email"],
            role=user["role"],
        )

    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    

def get_current_user_from_token(token: str) -> CurrentUser:
    try:
        payload = verify_supabase_jwt(token)

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role") or payload.get("app_metadata", {}).get("role", "user")

        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        user = get_user_by_id(user_id)

        if not user:
            user = create_user(
                user_id=user_id,
                email=email,
                role=role,
            )

        return CurrentUser(
            id=user["id"],
            email=user["email"],
            role=user["role"],
        )

    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

def get_current_vscode_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    token = credentials.credentials
    try:
        logger.info(f"[VSCodeAuth] Raw token (first 40 chars): {token[:40]}...")
        payload = jwt.decode(
            token,
            settings.VSCODE_JWT_SECRET,
            algorithms=["HS256"],
            audience="vscode-extension",
        )
        logger.info(f"[VSCodeAuth] Decoded payload: {payload}")
    except jwt.ExpiredSignatureError:
        logger.error("[VSCodeAuth] Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="VS Code session expired. Please login again.",
        )
    except jwt.InvalidAudienceError as e:
        logger.error(f"[VSCodeAuth] Invalid aud: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid VS Code token audience.",
        )
    except jwt.PyJWTError as e:
        logger.error(f"[VSCodeAuth] PyJWT error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid VS Code authentication token.",
        )

    user_id = payload.get("sub")
    if not user_id:
        logger.error("[VSCodeAuth] Missing sub in payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid VS Code token payload.",
        )

    user = get_user_by_id(user_id)
    if not user:
        logger.error(f"[VSCodeAuth] User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please login again via VS Code.",
        )

    return CurrentUser(
        id=user["id"],
        email=user["email"],
        role=user["role"],
    )