from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.connection import get_db
from backend.app.api.v1.dependencies import get_current_user
from backend.app.schemas.user_preferences import (UserPreferencesCreate, UserPreferencesResponse)
from backend.app.services.user_preferences_service import (get_user_preferences, create_user_preferences)

router = APIRouter(
    prefix="/users/me",
    tags=["User Preferences"]
)


@router.get("/preferences", response_model=UserPreferencesResponse)
async def check_user_preferences(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    preferences = await get_user_preferences(db, current_user.id)

    if not preferences:
        return {"exists": False}

    return {
        "exists": True,
        "preferences": preferences
    }


@router.post("/preferences")
async def save_user_preferences(
    payload: UserPreferencesCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    await create_user_preferences(
        db=db,
        user_id=current_user.id,
        data=payload.dict()
    )

    return {"message": "User preferences saved successfully"}
