import logging
import os

import sentry_sdk
from aiohttp import web
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from . import website

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger(__name__).setLevel(logging.DEBUG)


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        AioHttpIntegration(),
        LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
    ],
    release=os.getenv("PLATFORM_TREE_ID"),
    environment=os.getenv("PLATFORM_BRANCH"),
)


async def index(request: web.Request) -> web.HTTPFound:
    location = request.app["website_app"].router["index"].url_for()
    return web.HTTPFound(location=location)


async def app_factory() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index)

    website_app = website.app_factory()
    app.add_subapp("/web", website_app)
    app["website_app"] = website_app

    return app
