import os
from pathlib import Path

from aiohttp import ClientSession, web
from aiohttp_jinja2 import setup as jinja2_setup, request_processor
from aioredis.abc import AbcConnection as RedisConnection
from apscheduler.schedulers.base import BaseScheduler
from jinja2 import FileSystemLoader
from jinja2.filters import FILTERS

from .. import settings
from .contexts import background_jobs, slack_client
from .filters import formatted_number
from .views import routes  # , on_oauth2_login


async def app_factory(
    client_session: ClientSession, redis: RedisConnection, scheduler: BaseScheduler
) -> web.Application:
    package_root = Path(__file__).parent

    website = web.Application()
    website.update(  # pylint: disable=no-member
        client_session=client_session,
        redis=redis,
        scheduler=scheduler,
        slack_invite_token=settings.SLACK_INVITE_TOKEN,
        slack_token=settings.SLACK_TOKEN,
    )

    # aiohttp_jinja2 requires this values to be set. Sadly it does not work with subapplication.
    # We need to use request.app.router["static"].url_for(filename='images/pyslackers_small.svg')
    # in templates to get the correct url for static assets
    website["static_root_url"] = "DO-NOT-USE"

    jinja2_setup(
        website,
        context_processors=[request_processor],
        loader=FileSystemLoader(str(package_root / "templates")),
        filters={"formatted_number": formatted_number, **FILTERS},
    )

    # this ordering is important, before reordering be sure to check
    # for dependencies.
    website.cleanup_ctx.extend([slack_client, background_jobs])

    website.add_routes(routes)
    website.router.add_static("/static", package_root / "static", name="static")

    return website
