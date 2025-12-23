from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import text
from backend.app.api.v1.dependencies import get_current_user_from_token
from backend.app.core.config import get_settings
from fastapi import HTTPException, Request
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.connection import get_db
import json
from datetime import datetime, timedelta, timezone


router = APIRouter()
settings = get_settings()

#Oauth endpoint
@router.get("/users/me/connect/linkedin")
async def connect_linkedin(request: Request, db: AsyncSession = Depends(get_db)):
    access_token = request.query_params.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Missing access token")

    current_user = get_current_user_from_token(access_token)

    params = {
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "scope": "openid profile email w_member_social ",
        "state": str(current_user.id)
    }

    url = "https://www.linkedin.com/oauth/v2/authorization"
    redirect_url = url + "?" + "&".join(f"{k}={v}" for k, v in params.items())

    return RedirectResponse(redirect_url)

#callback endpoint
@router.get("/auth/linkedin/callback")
async def linkedin_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            },
        )

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    refresh_token = token_data.get("refresh_token") 
    expires_in = token_data.get("expires_in") # Seconds until access token expires
    
    token_expires_at = None
    if expires_in:
        # Calculate future timestamp
        token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    if not access_token:
        raise HTTPException(status_code=400, detail="LinkedIn OAuth failed")

# fetch LinkedIn profile
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient() as client:
        profile = (
            await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers=headers,
            )
        ).json()

#Store in connected_accounts
    await db.execute(
        text("""
        INSERT INTO connected_accounts
        (user_id, platform, access_token, refresh_token, token_expires_at, profile_id, profile_data)
        VALUES (:uid, 'linkedin', :token, :refresh, :expires, :pid, :pdata)
        ON CONFLICT (user_id, platform)
        DO UPDATE SET 
          access_token = EXCLUDED.access_token,
          refresh_token = EXCLUDED.refresh_token,
          token_expires_at = EXCLUDED.token_expires_at,
          profile_data = EXCLUDED.profile_data,
          connected_at = NOW()
        """),
        {
            "uid": state,
            "token": access_token,
            "refresh": refresh_token,
            "expires": token_expires_at,
            "pid": profile.get("sub"),
            "pdata": json.dumps(profile),
        },
    )

    await db.commit()

    return RedirectResponse(
        f"{settings.FRONTEND_URL}/settings?linkedin=connected"
    )
