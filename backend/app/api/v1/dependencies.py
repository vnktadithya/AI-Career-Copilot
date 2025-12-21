from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.core.security import verify_supabase_jwt, AuthError
from backend.app.models.user import CurrentUser
from backend.app.services.user_service import get_user_by_id, create_user

security = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
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
