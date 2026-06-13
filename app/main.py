from __future__ import annotations

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware




def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(api_router)
    return app


app = create_app()
