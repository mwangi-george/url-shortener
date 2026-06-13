from __future__ import annotations

import orjson
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware


class CustomORJSONResponse(ORJSONResponse):
    def render(self, content: object) -> bytes:
        return orjson.dumps(content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY)


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        default_response_class=CustomORJSONResponse,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(api_router)
    return app


app = create_app()
