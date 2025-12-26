# app/api/router.py
from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, users, repos, stories, webhooks, audit, health, user_preferences, github, linkedin, vscode_auth


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(user_preferences.router)
api_router.include_router(github.router, tags=["github"])
api_router.include_router(linkedin.router, tags=["linkedin"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(vscode_auth.router, prefix="/auth/vscode", tags=["vscode-auth"],)
