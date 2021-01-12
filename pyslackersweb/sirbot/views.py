import re
import asyncio
import logging

import slack.commands
import slack.actions
import slack.events

from aiohttp import web
from slack import methods
from slack.sansio import validate_request_signature

from pyslackersweb.util.log import ContextAwareLoggerAdapter
from pyslackersweb.sirbot import settings
from pyslackersweb.sirbot.slack import commands, actions, events, messages


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

        msg = events.Message()
        msg["channel"] = settings.READTHEDOCS_NOTIFICATION_CHANNEL
        msg["text"] = f"""Building of {project}@{commit} documentation {status} ! :{emoji}:"""

        await self.request.app["slack_client"].query(methods.CHAT_POST_MESSAGE, data=msg)

        return web.Response(status=200)


class SlackView(web.View):
    async def _validate_request(self):
        body = await self.request.read()
        validate_request_signature(
            body=body.decode("utf-8"),
            headers=dict(self.request.headers),
            signing_secret=settings.SLACK_SIGNING_SECRET,
        )

    def execute_handler(self, handler, *args) -> None:
        asyncio.create_task(self._exectute_handler(handler, *args))

    async def _exectute_handler(self, handler, *args) -> None:
        try:
            await handler(*args)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Failed to execute handler")

    async def post(self) -> web.Response:
        await self._validate_request()
        return web.Response(status=200)


@routes.view("/slack/commands", name="slack_commands")
class SlackCommandsView(SlackView):
    router = slack.commands.Router()
    router.register("/admin", commands.admin)
    router.register("/snippet", commands.snippet)
    router.register("/howtoask", commands.howto_ask)
    router.register("/justask", commands.ask_question)
    router.register("/sponsors", commands.sponsors)

    async def post(self) -> web.Response:
        await super().post()
        payload = dict(await self.request.post())
        cmd = slack.commands.Command(payload, team_id=settings.SLACK_TEAM_ID)
        for handler in self.router.dispatch(cmd):
            self.execute_handler(handler, self.request, cmd)
        return web.Response(status=200)


@routes.view("/slack/actions", name="slack_actions")
class SlackActionsView(SlackView):
    router = slack.actions.Router()
    router.register("admin", actions.admin_msg)

    router.register("topic_change", actions.topic_change_revert, name="revert")
    router.register("topic_change", actions.topic_change_validate, name="validate")
    router.register("purpose_change", actions.purpose_change_revert, name="revert")
    router.register("purpose_change", actions.purpose_change_validate, name="validate")
    router.register("pin_added", actions.pin_added_revert, name="revert")
    router.register("pin_added", actions.pin_added_validate, name="validate")
    router.register("inspect", actions.user_cleanup, name="user_cleanup")

    async def post(self) -> web.Response:
        await super().post()
        payload = dict(await self.request.post())
        action = slack.actions.Action.from_http(payload, team_id=settings.SLACK_TEAM_ID)
        for handler in self.router.dispatch(action):
            self.execute_handler(handler, self.request, action)
        return web.Response(status=200)


@routes.view("/slack/events", name="slack_events")
class SlackEventsView(SlackView):
    event_router = slack.events.EventRouter()
    event_router.register("team_join", events.team_join)
    event_router.register("pin_added", events.pin_added)

    msg_router = slack.events.MessageRouter()
    msg_router.register("hello", messages.hello, flags=re.IGNORECASE)
    msg_router.register(r"^(<@\w{9}> |)inspect", messages.inspect, flags=re.IGNORECASE)
    msg_router.register(messages.TELL_REGEX.pattern, messages.tell, flags=re.IGNORECASE)
    msg_router.register(messages.STOCK_REGEX.pattern, messages.stock_quote)

    msg_router.register(".*", messages.mention, flags=re.IGNORECASE)
    msg_router.register(".*", messages.store, flags=re.IGNORECASE)
    msg_router.register(".*", messages.channel_topic, subtype="channel_topic")
    msg_router.register(".*", messages.channel_purpose, subtype="channel_purpose")

    async def post(self) -> web.Response:
        await super().post()
        payload = await self.request.json()
        if payload["type"] == "url_verification":
            return web.Response(body=payload["challenge"])

        response = web.Response(status=200)
        event = slack.events.Event.from_http(payload, team_id=settings.SLACK_TEAM_ID)

        # Filter bot_message. We do not want to react to our own messages
        if event["type"] == "bot_message":
            return response
        if event.get("subtype") == "bot_message":
            return response

        if isinstance(event, slack.events.Message):
            for handler in self.msg_router.dispatch(event):
                self.execute_handler(handler, self.request, event)
        else:
            for handler in self.event_router.dispatch(event):
                self.execute_handler(handler, self.request, event)

        return response
