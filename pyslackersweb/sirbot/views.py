import logging

from aiohttp import web
from slack import methods
from slack.events import Message

from pyslackersweb.util.log import ContextAwareLoggerAdapter

from . import settings

logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))

routes = web.RouteTableDef()


@routes.view("/readthedocs", name="readthedocs")
class ReadTheDocsView(web.View):
    async def post(self):
        payload = await self.request.json()
        logger.debug("Incoming readthedocs notification: %s", payload)

        project = payload.get("name")
        if not project:
            return web.Response(status=400)

        build = payload.get("build")
        if not build:
            return web.Response(status=400)

        if build.get("state") != "finished":
            return web.Response(status=200)

        commit = build["commit"][:7]
        if build["success"]:
            status, emoji = "successful", "toot"
        else:
            status, emoji = "failed", "cry"

        msg = Message()
        msg["channel"] = settings.READTHEDOCS_NOTIFICATION_CHANNEL
        msg["text"] = f"""Building of {project}@{commit} documentation {status} ! :{emoji}:"""

        await self.request.app["slack_client"].query(methods.CHAT_POST_MESSAGE, data=msg)

        return web.Response(status=200)
