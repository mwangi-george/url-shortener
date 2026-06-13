from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import health, redirects, urls

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(urls.router, prefix="/api/v1", tags=["urls"])
api_router.include_router(redirects.router, tags=["redirects"])
