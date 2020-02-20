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

        project = payload.get("name")
        if not project:
            return web.Response(status=400)

        logger.debug("Incoming readthedocs notification: %s", payload)

        msg = Message()
        msg["channel"] = settings.READTHEDOCS_NOTIFICATION_CHANNEL
        msg["text"] = f"""Building of {project} documentation failed ! :cry:"""
        await self.request.app["slack_client"].query(methods.CHAT_POST_MESSAGE, data=msg)

        return web.Response(status=200)
