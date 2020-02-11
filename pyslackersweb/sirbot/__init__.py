from aiohttp import web

from .. import settings
from .views import routes  # , on_oauth2_login


async def app_factory() -> web.Application:
    sirbot = web.Application()
    sirbot.update(  # pylint: disable=no-member
        client_session=None,  # populated via parent app signal
        redis=None,  # populated via parent app signal
        scheduler=None,  # populated via parent app signal
        slack_invite_token=settings.SLACK_INVITE_TOKEN,
        slack_token=settings.SLACK_TOKEN,
    )

    sirbot.add_routes(routes)

    return sirbot
