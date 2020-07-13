import logging.config
import pathlib
import yaml

import sentry_sdk
from aiohttp import web
from aiohttp_remotes import XForwardedRelaxed, ForwardedRelaxed
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .contexts import (
    apscheduler,
    client_session,
    redis_pool,
    postgresql_pool,
    slack_client,
    background_jobs,
)
from .middleware import request_context_middleware
from . import settings, website, sirbot


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
        SqlalchemyIntegration(),
    ],
    release=settings.SENTRY_RELEASE,
    environment=settings.SENTRY_ENVIRONMENT,
)


async def index(request: web.Request) -> web.HTTPFound:
    location = request.app["subapps"]["website"].router["index"].url_for()
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
        subapps={},
        client_session=None,  # populated via signal
        scheduler=None,  # populated via signal
        redis=None,  # populated via signal
        db=None,  # populated via signal
        REDIS_URL=settings.REDIS_URL,
        DATABASE_URL=settings.DATABASE_URL,
        SLACK_INVITE_TOKEN=settings.SLACK_INVITE_TOKEN,
        SLACK_TOKEN=settings.SLACK_TOKEN,
    )

    app.cleanup_ctx.extend(
        [apscheduler, client_session, redis_pool, postgresql_pool, slack_client, background_jobs]
    )

    app.router.add_get("/", index)

    app["subapps"]["website"] = await website.app_factory()
    app.add_subapp("/web", app["subapps"]["website"])

    app["subapps"]["sirbot"] = await sirbot.app_factory()
    app.add_subapp("/bot", app["subapps"]["sirbot"])

    return app
