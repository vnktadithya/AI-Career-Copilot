from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging
from backend.app.api.v1.dependencies import get_current_vscode_user
from backend.app.database.supabase_client import supabase_service
from supabase import create_client, Client
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)
router = APIRouter()


class VSCodeEventIn(BaseModel):
    """Schema for VS Code extension event ingestion."""
    event_type: str = Field(..., example="working_tree_changed")
    payload: Dict[str, Any] = Field(..., example={"filePath": "/src/main.ts"})
    timestamp: str = Field(..., example="2025-12-25T10:30:00Z")
    dedupe_key: str = Field(..., description="Hash to prevent duplicates")


@router.post("/vscode", status_code=status.HTTP_200_OK)
def ingest_vscode_event(
    event: VSCodeEventIn,
    current_user=Depends(get_current_vscode_user),
):
    """
    Ingests developer activity events from the VS Code extension.
    Uses service role client to bypass RLS.
    """
    
    user_id = str(current_user.id)
    
    logger.info(
        f"📥 Received VS Code event: user_id={user_id}, type={event.event_type}"
    )
    
    payload = {
        "user_id": user_id,
        "repo_id": None,
        "event_type": event.event_type,
        "event_source": "vscode_extension",
        "payload": event.payload,
        "processed": False,
        "dedupe_key": event.dedupe_key,
    }
    
    if not supabase_service:
        logger.error("❌ Service role client not initialized")
        raise HTTPException(
            status_code=500,
            detail="Service client not configured. Set SUPABASE_SERVICE_ROLE_KEY in .env"
        )
    
    try:
        response = supabase_service.table("activity_events").insert(payload).execute()
        
        if response.data:
            event_id = response.data[0].get("id")
            logger.info(f"✅ Activity event stored: {event_id}")
            return {"status": "stored", "event_id": event_id}
        else:
            return {"status": "stored"}
        
    except APIError as e:
        error_msg = str(e)
        logger.error(f"❌ Database error: {error_msg}")
        
        # ✅ HANDLE DUPLICATE (SILENTLY - expected behavior)
        if "duplicate key value" in error_msg or "dedupe_key_key" in error_msg or "already exists" in error_msg:
            logger.info(f"⚠️ Duplicate event ignored (dedupe_key): {event.dedupe_key[:8]}...")
            return {"status": "stored", "duplicate": True}  # ✅ TREAT AS SUCCESS
        
        # ❌ REAL ERRORS (RLS, network, etc.)
        if "permission denied" in error_msg.lower():
            logger.error("❌ RLS denied. Check SERVICE_ROLE_KEY configuration")
            raise HTTPException(status_code=403, detail="Database permission denied.")
        
        logger.exception(f"❌ Unexpected error")
        raise HTTPException(status_code=500, detail=f"Failed to store event: {error_msg}")



@router.get("/vscode/health")
def webhook_health():
    """Health check endpoint."""
    return {"status": "ok", "service": "activity_events_webhook"}