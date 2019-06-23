import os
from pathlib import Path

from aiohttp import web
from aiohttp_jinja2 import setup as jinja2_setup, request_processor
from jinja2 import FileSystemLoader
from jinja2.filters import FILTERS

from .contexts import apscheduler, background_jobs, client_session, redis, slack_client
from .filters import formatted_number
from .views import routes  # , on_oauth2_login


def app_factory() -> web.Application:
    package_root = Path(__file__).parent

    website = web.Application()
    website.update(  # pylint: disable=no-member
        redis_uri=os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
        slack_invite_token=os.getenv("SLACK_INVITE_TOKEN", os.getenv("SLACK_OAUTH_TOKEN")),
        slack_timezones={},
        slack_token=os.getenv("SLACK_TOKEN", os.getenv("SLACK_OAUTH_TOKEN")),
        slack_user_count=0,
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
    website.cleanup_ctx.extend([apscheduler, client_session, slack_client, redis, background_jobs])

    website.add_routes(routes)
    website.router.add_static("/static", package_root / "static", name="static")

    return website
