import logging
import os

import aioredis
import sentry_sdk
from aiohttp import ClientSession, web
from aiohttp_remotes import XForwardedRelaxed, ForwardedRelaxed
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .contexts import apscheduler, close_client_session, close_redis
from .middleware import request_context_middleware
from . import settings, website

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger(__name__).setLevel(logging.DEBUG)


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[
        AioHttpIntegration(),
        LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
    ],
    release=settings.SENTRY_RELEASE,
    environment=settings.SENTRY_ENVIRONMENT,
)


async def index(request: web.Request) -> web.HTTPFound:
    location = request.app["website_app"].router["index"].url_for()
    return web.HTTPFound(location=location)


async def app_factory() -> web.Application:
    app = web.Application(
        middlewares=[
            ForwardedRelaxed().middleware,
            XForwardedRelaxed().middleware,
            request_context_middleware,
        ]
    )
    app.update(  # pylint: disable=no-member
        client_session=ClientSession(),
        scheduler=AsyncIOScheduler(),
        redis=await aioredis.create_redis_pool(settings.REDIS_URL),
    )

    app.cleanup_ctx.append(apscheduler)
    app.on_cleanup.extend([close_client_session, close_redis])

    app.router.add_get("/", index)

    app["website_app"] = website_app = await website.app_factory(
        app["client_session"], app["redis"], app["scheduler"]
    )
    app.add_subapp("/web", website_app)

    return app
