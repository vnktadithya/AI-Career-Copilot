from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from backend.app.core.redis import redis_client
from backend.app.core.config import get_settings
from backend.app.services.vscode_auth_service import issue_vscode_session_jwt
from backend.app.services.user_service import get_user_by_id, create_user
from backend.app.database.supabase_client import supabase
import json
import uuid
from datetime import datetime, timezone

router = APIRouter()
settings = get_settings()

SUPABASE_URL = settings.SUPABASE_URL
BACKEND_URL = settings.BACKEND_URL

LOGIN_TTL_SECONDS = 300  # 5 minutes


@router.post("/login")
def vscode_login():
    """
    Step 1: Create a temporary VS Code login session in Redis
    """
    session_id = str(uuid.uuid4())
    key = f"vscode:login:{session_id}"
    
    redis_client.setex(
        key,
        LOGIN_TTL_SECONDS,
        json.dumps({
            "status": "pending",
            "provider": "github",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    )

    clean_backend_url = (str(BACKEND_URL)).rstrip("/")
    # --- FIX: Use Path Parameter (Slash) ---
    base_redirect = f"{clean_backend_url}/api/v1/auth/vscode/callback"
    
    # We append the ID directly with a slash. 
    # Example: http://127.0.0.1:8000/api/v1/auth/vscode/callback/a3edb152...
    redirect_url = f"{base_redirect}/{session_id}"

    auth_url = (
        f"{SUPABASE_URL}/auth/v1/authorize"
        f"?provider=github"
        f"&redirect_to={redirect_url}"
    )

    return {
        "auth_url": auth_url,
        "session_id": session_id
    }


# --- FIX: Update Route to accept Path Parameter ---
@router.get("/callback/{client_state}") 
def vscode_callback(client_state: str):
    """
    Supabase redirects here: /callback/<session_id>#access_token=...
    We capture <session_id> from the URL path as 'client_state'.
    """
    clean_backend_url = str(BACKEND_URL).rstrip("/")
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="background-color: #1e1e1e; color: #d4d4d4; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh;">
    <div id="msg" style="text-align: center;">Finalizing login...</div>
    <script>
        const hash = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hash.get("access_token");

        if (!accessToken) {{
            document.getElementById("msg").innerText = "Login failed: no access token found.";
        }} else {{
            // We use the 'client_state' (session_id) captured from the python function
            fetch("{clean_backend_url}/api/v1/auth/vscode/complete", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{
                    state: "{client_state}", 
                    access_token: accessToken
                }})
            }})
            .then(() => {{
                document.getElementById("msg").innerText = "Success! You can close this tab and return to VS Code.";
            }})
            .catch((err) => {{
                document.getElementById("msg").innerText = "Error connecting to backend.";
                console.error(err);
            }});
        }}
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


@router.post("/complete")
def vscode_complete_login(payload: dict):
    """
    Step 3: Finalize login and Sync user to local DB
    """
    state = payload["state"]
    access_token = payload["access_token"]
    
    # 1. Verify Supabase token
    try:
        user_response = supabase.auth.get_user(access_token)
        user = user_response.user
        user_id = user.id
        email = user.email
    except Exception as e:
        print(f"--- DEBUG ERROR: {str(e)} ---") 
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

    # 2. Sync User to Local DB using SERVICE ROLE (Admin)
    try:
        local_user = get_user_by_id(user_id)
        if not local_user:
            print(f"Creating new local user for {email}")
            create_user(user_id=user_id, email=email, role="user")
            print("✅ User created successfully")

    except Exception as e:
        # If it fails now, it's a real issue, not just permissions
        print(f"Error syncing user: {e}")
        # We don't raise here to allow the login flow to complete, 
        # but the webhook might fail later if this didn't work.
        pass

    key = f"vscode:login:{state}"
    
    redis_client.setex(
        key,
        LOGIN_TTL_SECONDS,
        json.dumps({
            "status": "completed",
            "user_id": user_id,
            "completed_at": datetime.now(timezone.utc).isoformat()
        })
    )

    return {"status": "ok"}


@router.get("/session/{session_id}")
def poll_session(session_id: str):
    """
    Step 4: VS Code polls this endpoint
    """
    key = f"vscode:login:{session_id}"
    raw = redis_client.get(key)

    if not raw:
        return {"status": "expired"}

    data = json.loads(raw)

    if data["status"] != "completed":
        return {"status": "pending"}

    session_token = issue_vscode_session_jwt(data["user_id"])

    return {
        "status": "completed",
        "session_token": session_token,
        "user_id": data["user_id"]
    }
