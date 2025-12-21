from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class CurrentUser(BaseModel):
    id: UUID
    email: str
    role: str = "user"
