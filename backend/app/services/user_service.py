from typing import Optional
from uuid import UUID
from backend.app.database.supabase_client import supabase


def get_user_by_id(user_id: UUID) -> Optional[dict]:
    response = (
        supabase
        .table("users")
        .select("*")
        .eq("id", str(user_id))
        .maybe_single()
        .execute()
    )

    # Supabase client variations:
    # - response may be None
    # - response may be APIResponse with .data
    if response is None:
        return None

    data = getattr(response, "data", None)
    return data


def create_user(
    *,
    user_id: UUID,
    email: str,
    name: Optional[str] = None,
    role: str = "user",
) -> dict:
    response = (
        supabase
        .table("users")
        .insert({
            "id": str(user_id),
            "email": email,
            "name": name,
            "role": role,
        })
        .execute()
    )

    data = getattr(response, "data", None)

    if not data or not isinstance(data, list):
        raise RuntimeError("Failed to create user in database")

    return data[0]
