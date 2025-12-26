import jwt
from datetime import datetime, timedelta, timezone
from backend.app.core.config import get_settings

JWT_TTL_MINUTES = 30
settings = get_settings()

def issue_vscode_session_jwt(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "iss": "career-story-os",
        "aud": "vscode-extension",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_TTL_MINUTES),
        "scope": "vscode"
    }

    token = jwt.encode(
        payload,
        settings.VSCODE_JWT_SECRET,
        algorithm="HS256"
    )

    return token
