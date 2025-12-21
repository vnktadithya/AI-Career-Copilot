from jose import jwt, JWTError
from typing import Dict, Any
from backend.app.core.config import get_settings

settings = get_settings()


class AuthError(Exception):
    pass


def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    """
    Verify Supabase JWT using HS256 + JWT secret.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience=settings.SUPABASE_JWT_AUDIENCE,
        )
        return payload
    except JWTError as e:
        raise AuthError(f"Invalid token: {str(e)}") from e
