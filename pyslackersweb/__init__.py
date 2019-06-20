import logging
import os
from pathlib import Path

import sentry_sdk
from aiohttp import web
from aiohttp_jinja2 import setup as jinja2_setup, request_processor
from aiohttp_remotes import XForwardedRelaxed, ForwardedRelaxed
from jinja2 import FileSystemLoader
from jinja2.filters import FILTERS
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from .contexts import background_jobs, client_session
from .filters import formatted_number
from .middleware import request_context_middleware
from .views import routes  # , on_oauth2_login

logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__).setLevel(logging.DEBUG)


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        AioHttpIntegration(),
        LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
    ],
    release=os.getenv("PLATFORM_TREE_ID"),
    environment=os.getenv("PLATFORM_ENVIRONMENT"),
)


async def app_factory() -> web.Application:
    package_root = Path(__file__).parent

    app = web.Application(
        middlewares=[
            ForwardedRelaxed().middleware,
            XForwardedRelaxed().middleware,
            request_context_middleware,
        ]
    )
    app.update(  # pylint: disable=no-member
        static_root_url="/static",
        github_repositories=[],
        slack_user_count=0,
        slack_timezones={},
        slack_token=os.getenv("SLACK_TOKEN", os.getenv("SLACK_OAUTH_TOKEN")),
        slack_invite_token=os.getenv("SLACK_INVITE_TOKEN", os.getenv("SLACK_OAUTH_TOKEN")),
    )

    jinja2_setup(
        app,
        context_processors=[request_processor],
        loader=FileSystemLoader([package_root / "templates"]),
        filters={"formatted_number": formatted_number, **FILTERS},
    )

    app.cleanup_ctx.append(client_session)
    app.cleanup_ctx.append(background_jobs)

    app.add_routes(routes)
    app.router.add_static(app["static_root_url"], package_root / "static")

    return app
