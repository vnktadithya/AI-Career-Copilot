from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class UserPreferencesCreate(BaseModel):
    tone: str
    include_emojis: bool
    portfolio_repo_url: Optional[str] = None
    portfolio_branch: Optional[str] = None
    auto_deploy: bool

    # 🔥 ALWAYS A DICT
    sample_posts: Dict[str, List[str]] = Field(default_factory=dict)


class UserPreferencesResponse(BaseModel):
    exists: bool
    preferences: Optional[UserPreferencesCreate] = None
