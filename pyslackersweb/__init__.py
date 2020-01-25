import logging
import logging.config
import os
import pathlib
import yaml

import aioredis
import sentry_sdk
from aiohttp import ClientSession, web
from aiohttp_remotes import XForwardedRelaxed, ForwardedRelaxed
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .contexts import apscheduler, client_session, redis_pool, postgresql_pool
from .middleware import request_context_middleware
from . import settings, website


logging_configuration = pathlib.Path(__file__).parents[1] / "logging.yml"
with open(logging_configuration, "r") as f:
    config = yaml.safe_load(f)

logging.config.dictConfig(config)
logging.captureWarnings(True)

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[
        AioHttpIntegration(),
        LoggingIntegration(level=logging.DEBUG, event_level=logging.WARNING),
    ],
    release=settings.SENTRY_RELEASE,
    environment=settings.SENTRY_ENVIRONMENT,
)


async def index(request: web.Request) -> web.HTTPFound:
    location = request.app["website_app"].router["index"].url_for()
    return web.HTTPFound(location=location)


async def app_factory(*args) -> web.Application:  # pylint: disable=unused-argument
    app = web.Application(
        middlewares=[
            ForwardedRelaxed().middleware,
            XForwardedRelaxed().middleware,
            request_context_middleware,
        ]
    )
    app.update(  # pylint: disable=no-member
        client_session=None,  # populated via signal
        scheduler=None,  # populated via signal
        redis=None,  # populated via signal
        db=None,  # populated via signal
        REDIS_URL=settings.REDIS_URL,
        DATABASE_URL=settings.DATABASE_URL,
        DISABLE_INVITES=settings.DISABLE_INVITES,
    )

    app.cleanup_ctx.extend([apscheduler, client_session, redis_pool, postgresql_pool])

    app.router.add_get("/", index)

    app["website_app"] = await website.app_factory()
    app.add_subapp("/web", app["website_app"])

    return app
