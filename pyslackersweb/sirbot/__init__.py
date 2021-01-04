from aiohttp import web

from .views import routes
from .context import background_jobs


async def app_factory() -> web.Application:
    sirbot = web.Application()
    sirbot.update(  # pylint: disable=no-member
        client_session=None,  # populated via parent app signal
        redis=None,  # populated via parent app signal
        scheduler=None,  # populated via parent app signal
    )

    sirbot.add_routes(routes)

    sirbot.cleanup_ctx.extend([background_jobs])

    return sirbot
