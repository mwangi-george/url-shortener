from __future__ import annotations

import logging
import sys

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def configure_logging() -> None:
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.log_level)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        serialize=settings.app_env == "prod",
        backtrace=False,
        diagnose=settings.debug,
    )
