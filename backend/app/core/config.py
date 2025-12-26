from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from functools import lru_cache
import os

# This finds the folder where this config.py lives
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# This points to the .env file in your backend root
ENV_PATH = os.path.join(CURRENT_DIR, "../../.env")

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: AnyHttpUrl
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_JWT_AUDIENCE: str = "authenticated"

    # Environment
    ENV: str = "development"

    # 🔑 GitHub OAuth (required for Option A)
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: AnyHttpUrl

    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: str
    LINKEDIN_CLIENT_SECRET: str
    LINKEDIN_REDIRECT_URI: AnyHttpUrl

    # Frontend & Backend
    FRONTEND_URL: AnyHttpUrl
    BACKEND_URL: AnyHttpUrl

    # VS Code JWT
    VSCODE_JWT_SECRET: str

    # Pydantic V2 Configuration
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,            # Path to your .env file
        env_file_encoding="utf-8", 
        case_sensitive=True,       # Ensures SUPABASE_URL matches SUPABASE_URL
        extra="ignore"             # Ignores other vars in .env that aren't defined here
    )

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.SUPABASE_URL = str(settings.SUPABASE_URL).rstrip("/")
    return settings

# To test if it's working, you can uncomment these lines:
# settings = get_settings()
# print(f"Connecting to Supabase at: {settings.SUPABASE_URL}")