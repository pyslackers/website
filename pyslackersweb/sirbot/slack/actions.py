import json
import logging
import asyncio

from aiohttp import web
from slack import methods
from slack import actions
from slack.events import Message
from slack.exceptions import SlackAPIError, RateLimited

from pyslackersweb.sirbot import settings, models
from pyslackersweb.util.log import ContextAwareLoggerAdapter

logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


async def topic_change_revert(request: web.Request, action: actions.Action) -> None:
    response = Message()
    response["channel"] = action["channel"]["id"]
    response["ts"] = action["message_ts"]
    response["attachments"] = action["original_message"]["attachments"]
    response["attachments"][0]["color"] = "danger"
    response["attachments"][0]["text"] = f'Change reverted by <@{action["user"]["id"]}>'
    del response["attachments"][0]["actions"]

    data = json.loads(action["actions"][0]["value"])
    await request.app["slack_client"].query(
        url=methods.CHANNELS_SET_TOPIC,
        data={"channel": data["channel"], "topic": data["old_topic"]},
    )

    await request.app["slack_client"].query(url=action["response_url"], data=response)


async def topic_change_validate(request: web.Request, action: actions.Action) -> None:
    response = Message()
    response["channel"] = action["channel"]["id"]
    response["ts"] = action["message_ts"]
    response["attachments"] = action["original_message"]["attachments"]
    response["attachments"][0]["color"] = "good"
    response["attachments"][0]["text"] = f'Change validated by <@{action["user"]["id"]}>'
    del response["attachments"][0]["actions"]

    await request.app["slack_client"].query(url=action["response_url"], data=response)


async def purpose_change_revert(request: web.Request, action: actions.Action) -> None:
    response = Message()
    response["channel"] = action["channel"]["id"]
    response["ts"] = action["message_ts"]
    response["attachments"] = action["original_message"]["attachments"]
    response["attachments"][0]["color"] = "danger"
    response["attachments"][0]["text"] = f'Change reverted by <@{action["user"]["id"]}>'
    del response["attachments"][0]["actions"]

    data = json.loads(action["actions"][0]["value"])
    await request.app["slack_client"].query(
        url=methods.CHANNELS_SET_PURPOSE,
        data={"channel": data["channel"], "purpose": data["old_purpose"]},
    )

    await request.app["slack_client"].query(url=action["response_url"], data=response)


async def purpose_change_validate(request: web.Request, action: actions.Action) -> None:
    response = Message()
    response["channel"] = action["channel"]["id"]
    response["ts"] = action["message_ts"]
    response["attachments"] = action["original_message"]["attachments"]
    response["attachments"][0]["color"] = "good"
    response["attachments"][0]["text"] = f'Change validated by <@{action["user"]["id"]}>'
    del response["attachments"][0]["actions"]

    await request.app["slack_client"].query(url=action["response_url"], data=response)


async def pin_added_validate(request: web.Request, action: actions.Action) -> None:
    response = Message()
    response["channel"] = action["channel"]["id"]
    response["ts"] = action["message_ts"]
    response["attachments"] = action["original_message"]["attachments"]
    response["attachments"][0]["color"] = "good"
    response["attachments"][0]["pretext"] = f'Pin validated by <@{action["user"]["id"]}>'
    del response["attachments"][0]["actions"]

    await request.app["slack_client"].query(url=action["response_url"], data=response)


async def pin_added_revert(request: web.Request, action: actions.Action) -> None:
    response = Message()

    response["channel"] = action["channel"]["id"]
    response["ts"] = action["message_ts"]
    response["attachments"] = action["original_message"]["attachments"]
    response["attachments"][0]["color"] = "danger"
    response["attachments"][0]["pretext"] = f'Pin reverted by <@{action["user"]["id"]}>'
    del response["attachments"][0]["actions"]

    action_data = json.loads(action["actions"][0]["value"])
    remove_data = {"channel": action_data["channel"]}

    if action_data["item_type"] == "message":
        remove_data["timestamp"] = action_data["item_id"]
    elif action_data["item_type"] == "file":
        remove_data["file"] = action_data["item_id"]
    elif action_data["item_type"] == "file_comment":
        remove_data["file_comment"] = action_data["item_id"]
    else:
        raise TypeError(f'Unknown pin type: {action_data["type"]}')

    try:
        await request.app["slack_client"].query(url=methods.PINS_REMOVE, data=remove_data)
    except SlackAPIError as e:
        if e.error != "no_pin":
            raise

    await request.app["slack_client"].query(url=action["response_url"], data=response)


async def admin_msg(request: web.Request, action: actions.Action) -> None:
    admin_msg = Message()
    admin_msg["channel"] = settings.SLACK_ADMIN_CHANNEL
    admin_msg["attachments"] = [
        {
            "fallback": f'Message from {action["user"]["name"]}',
            "title": f'Message from <@{action["user"]["id"]}>',
            "color": "good",
            "text": action["submission"]["message"],
        }
    ]

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=admin_msg)

    response = Message()
    response["response_type"] = "ephemeral"
    response["text"] = "Thank you for your message."

    await request.app["slack_client"].query(url=action["response_url"], data=response)


async def user_cleanup(request: web.Request, action: actions.Action) -> None:
    user_id = action["actions"][0]["value"]

    response = Message()
    response["text"] = f"Cleanup of <@{user_id}> triggered by <@{action['user']['id']}>"

    await request.app["slack_client"].query(url=action["response_url"], data=response)

    asyncio.create_task(_cleanup_user(request.app, user_id))


async def _cleanup_user(app: web.Application, user: str) -> None:
    try:
        async with app["pg"].acquire() as conn:
            messages = await conn.fetch(
                """SELECT id, channel FROM slack_messages WHERE "user" = $1 ORDER BY send_at DESC""",
                user,
            )

        for message in messages:
            await _delete_message(app["slack_client"], message)
    except Exception:
        logger.exception("Unexpected exception cleaning up user %s", user)


async def _delete_message(slack, message: dict) -> None:
    data = {"channel": message["channel"], "ts": message["id"]}
    try:
        await slack.query(url=methods.CHAT_DELETE, data=data)
    except RateLimited:
        logger.debug("sleeping")
        await asyncio.sleep(20)
        await _delete_message(slack, message)
    except SlackAPIError as e:
        if e.error == "message_not_found":
            return
        else:
            logger.exception(
                "Failed to cleanup message %s in channel %s",
                message["id"],
                message["channel"],
            )
    except Exception:
        logger.exception(
            "Failed to cleanup message %s in channel %s",
            message["id"],
            message["channel"],
        )
