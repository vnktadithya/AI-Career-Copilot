from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.connection import get_db
from backend.app.core.config import get_settings
from backend.app.services.github_service import sync_github_account
from uuid import UUID
# refresh token not required as the access token will not expire

router = APIRouter()
settings = get_settings()

@router.get("/users/me/connect/github")
async def connect_github(state: str):
    
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "repo read:user",
        "state": state,
    }

    url = "https://github.com/login/oauth/authorize"
    redirect_url = f"{url}?" + "&".join(f"{k}={v}" for k, v in params.items())

    return RedirectResponse(redirect_url)

@router.get("/auth/github/callback")
async def github_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db)
):
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            }
        )

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    scope = token_data.get("scope")


    if not access_token:
        raise HTTPException(status_code=400, detail="GitHub OAuth failed")
    
    user_id = UUID(state)
    await sync_github_account(
        db=db,
        user_id=user_id,
        access_token=access_token,
        token_scope=scope
    )


    return RedirectResponse(str(settings.FRONTEND_URL) + "/settings?github=connected")
