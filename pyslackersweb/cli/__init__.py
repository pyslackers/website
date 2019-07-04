import sys
import logging
import contextlib

from typing import AsyncGenerator, List

from aiohttp import web

from pyslackersweb.cli import migrate
from pyslackersweb.util.log import ContextAwareLoggerAdapter

logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


@contextlib.asynccontextmanager
async def start_app(app: web.Application) -> AsyncGenerator[None, None]:
    logger.info("Starting cli application")
    runner = web.AppRunner(app)
    await runner.setup()

    yield

    await runner.cleanup()


def in_cli():
    return "gunicorn" not in sys.argv[0]
