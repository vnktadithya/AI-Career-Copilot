# app/api/router.py
from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, users, repos, stories, webhooks, audit, health
from backend.app.api.v1.endpoints import user_preferences


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(user_preferences.router)
