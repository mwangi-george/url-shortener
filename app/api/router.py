from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import health, redirects, urls

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(urls.router, tags=["urls"])
api_router.include_router(redirects.router, tags=["redirects"])
