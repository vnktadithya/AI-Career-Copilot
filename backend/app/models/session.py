from pydantic import BaseModel
from uuid import UUID


class SessionResponse(BaseModel):
    user_id: UUID
    email: str
    role: str
    is_new_user: bool
