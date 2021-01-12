import re
import json
import logging
import datetime

import asyncpg
import sqlalchemy as sa

from aiohttp import web, ClientResponseError
from decimal import Decimal
from slack import methods
from slack.exceptions import SlackAPIError
from slack.events import Message
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pyslackersweb.models import SlackChannels
from pyslackersweb.sirbot import settings, models, database
from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))
STOCK_REGEX = re.compile(r"\b(?P<asset_class>[cs])\$(?P<symbol>\^?[A-Z.]{1,5})\b")
TELL_REGEX = re.compile("tell (<(#|@)(?P<to_id>[A-Z0-9]*)(|.*)?>) (?P<msg>.*)")


async def stock_quote(request: web.Request, message: Message) -> None:
    match = STOCK_REGEX.search(message.get("text", ""))
    if not match:
        return

    asset_class, symbol = match.group("asset_class"), match.group("symbol")
    logger.debug("Fetching stock quotes for symbol %s in asset class %s", symbol, asset_class)

    if asset_class == "c":
        logger.debug("Fetching a crypto quote, appending USD as the pair's quote price.")
        symbol += "-USD"

    response = message.response()
    try:
        async with request.app["client_session"].get(
            "https://query1.finance.yahoo.com/v7/finance/quote",
            params={"symbols": symbol},
        ) as r:
            r.raise_for_status()
            body = (await r.json())["quoteResponse"]["result"]
            if len(body) < 1:
                return None

            quote = models.StockQuote(
                symbol=body[0]["symbol"],
                company=body[0].get("longName", body[0].get("shortName", "")),
                price=Decimal(body[0].get("regularMarketPrice", 0)),
                change=Decimal(body[0].get("regularMarketChange", 0)),
                change_percent=Decimal(body[0].get("regularMarketChangePercent", 0)),
                market_open=Decimal(body[0].get("regularMarketOpen", 0)),
                market_close=Decimal(body[0].get("regularMarketPreviousClose", 0)),
                high=Decimal(body[0].get("regularMarketDayHigh", 0)),
                low=Decimal(body[0].get("regularMarketDayLow", 0)),
                volume=Decimal(body[0].get("regularMarketVolume", 0)),
                time=datetime.datetime.fromtimestamp(body[0].get("regularMarketTime", 0)),
                logo=body[0].get("coinImageUrl"),
            )
    except ClientResponseError as e:
        if e.status == 404:
            response["text"] = f"Unable to find ticker {symbol}"
        else:
            logger.exception("Error retrieving stock quotes.")
            response["text"] = "Unable to retrieve quotes right now."
    else:
        if quote is None:
            response["text"] = f"Unable to find ticker '{symbol}'"
        else:
            color = "gray"
            if quote.change > 0:
                color = "good"
            elif quote.change < 0:
                color = "danger"

            response.update(
                attachments=[
                    {
                        "color": color,
                        "title": f"{quote.symbol} ({quote.company}): ${quote.price:,.4f}",
                        "title_link": f"https://finance.yahoo.com/quote/{quote.symbol}",
                        "fields": [
                            {
                                "title": "Change",
                                "value": f"${quote.change:,.4f} ({quote.change_percent:,.4f}%)",
                                "short": True,
                            },
                            {
                                "title": "Volume",
                                "value": f"{quote.volume:,}",
                                "short": True,
                            },
                            {
                                "title": "Open",
                                "value": f"${quote.market_open:,.4f}",
                                "short": True,
                            },
                            {
                                "title": "Close",
                                "value": f"${quote.market_close:,.4f}",
                                "short": True,
                            },
                            {
                                "title": "Low",
                                "value": f"${quote.low:,.4f}",
                                "short": True,
                            },
                            {
                                "title": "High",
                                "value": f"${quote.high:,.4f}",
                                "short": True,
                            },
                        ],
                        "footer_icon": quote.logo,
                        "ts": int(quote.time.timestamp()),
                    }
                ]
            )

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)


async def hello(request: web.Request, message: Message) -> None:
    if message.mention:
        response = message.response()
        response["text"] = "Hello <@{user}>".format(user=message["user"])
        await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)


async def store(request: web.Request, message: Message) -> None:
    if message.get("subtype") in ("message_deleted",):
        return

    timestamp, _ = message["ts"].split(".")
    send_at = datetime.datetime.fromtimestamp(int(timestamp))
    try:
        async with request.app["pg"].acquire() as conn:
            await conn.execute(
                pg_insert(models.SlackMessage).values(
                    id=message["ts"],
                    send_at=send_at,
                    user=message.get("user"),
                    channel=message["channel"],
                    message=message.get("text", ""),
                    raw=dict(message),
                )
            )
    except asyncpg.exceptions.UniqueViolationError as e:
        if "slack_messages_pkey" not in str(e):
            raise
    except Exception:
        logger.exception("Failed to store message: %s", message)


async def tell(request: web.Request, message: Message) -> None:
    if message.mention:
        match = TELL_REGEX.search(message["text"])
        response = message.response()

        if match:
            to_id = match.group("to_id")
            msg = match.group("msg")

            if to_id.startswith(("C", "U")):
                response["text"] = msg
                response["channel"] = to_id
            else:
                response["text"] = "Sorry I can not understand the destination."
        else:
            response["text"] = "Sorry I can not understand"

        await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)


async def mention(request: web.Request, message: Message) -> None:
    if message["type"] == "app_mention":
        try:
            await request.app["slack_client"].query(
                url=methods.REACTIONS_ADD,
                data={
                    "name": "sirbot",
                    "channel": message["channel"],
                    "timestamp": message["ts"],
                },
            )
        except SlackAPIError as e:
            if e.error != "already_reacted":
                raise


async def channel_topic(request: web.Request, message: Message) -> None:
    async with request.app["pg"].acquire() as conn:
        if database.is_admin(conn, message["user"]):
            return

    async with request.app["pg"].acquire() as conn:
        old_topic = await conn.fetchval(
            """SELECT topic FROM slack_channels WHERE id=$1""", message["channel"]
        )

    has_old_topic = True
    if not old_topic:
        has_old_topic = False
        old_topic = "Original topic not found"

    response = Message()
    response["channel"] = settings.SLACK_ADMIN_CHANNEL
    response["attachments"] = [
        {
            "fallback": f"Channel topic changed notice: {old_topic}",
            "title": f'<@{message["user"]}> changed <#{message["channel"]}> topic.',
            "fields": [
                {"title": "Previous topic", "value": old_topic},
                {"title": "New topic", "value": message["topic"]},
            ],
        }
    ]

    if has_old_topic:
        response["attachments"][0]["callback_id"] = "topic_change"
        response["attachments"][0]["actions"] = [
            {
                "name": "validate",
                "text": "Validate",
                "style": "primary",
                "type": "button",
            },
            {
                "name": "revert",
                "text": "Revert",
                "style": "danger",
                "value": json.dumps({"channel": message["channel"], "old_topic": old_topic}),
                "type": "button",
            },
        ]

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)


async def channel_purpose(request: web.Request, message: Message) -> None:
    async with request.app["pg"].acquire() as conn:
        if database.is_admin(conn, message["user"]):
            return

    async with request.app["pg"].acquire() as conn:
        old_purpose = await conn.fetchval(
            """SELECT purpose FROM slack_channels WHERE id=$1""", message["channel"]
        )

    # Do not re-trigger when we revert a change
    if old_purpose and old_purpose == message["purpose"]:
        return

    has_old_purpose = True
    if not old_purpose:
        has_old_purpose = False
        old_purpose = "Original topic not found"

    response = Message()
    response["channel"] = settings.SLACK_ADMIN_CHANNEL
    response["attachments"] = [
        {
            "fallback": f"Channel purpose changed notice: {old_purpose}",
            "title": f'<@{message["user"]}> changed <#{message["channel"]}> purpose.',
            "fields": [
                {"title": "Previous purpose", "value": old_purpose},
                {"title": "New purpose", "value": message["purpose"]},
            ],
        }
    ]

    if has_old_purpose:
        response["attachments"][0]["callback_id"] = "purpose_change"
        response["attachments"][0]["actions"] = [
            {
                "name": "validate",
                "text": "Validate",
                "style": "primary",
                "type": "button",
            },
            {
                "name": "revert",
                "text": "Revert",
                "style": "danger",
                "value": json.dumps({"channel": message["channel"], "old_purpose": old_purpose}),
                "type": "button",
            },
        ]

    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)


async def inspect(request: web.Request, message: Message) -> None:
    if (
        not message.mention
        or message["channel"] != settings.SLACK_ADMIN_CHANNEL
        or "text" not in message
        or not message["text"]
    ):
        return

    response = message.response()
    matches = re.findall("<@(\w*)>", message["text"])
    if matches is None:
        response["text"] = f"Sorry I couldn't figure out which user to inspect"
        await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)
        return

    if len(matches) == 1:
        user_id = matches[0]
    else:
        user_id = matches[1]

    async with request.app["pg"].acquire() as conn:
        local_dump = await conn.fetchrow(
            """
SELECT first_seen, (SELECT count(id) FROM slack_messages WHERE "user" = $1) as total_messages,
 send_at as last_message_ts, message as last_message_text, slack_channels.name as last_message_channel
FROM slack_users
JOIN slack_messages ON slack_users.id = slack_messages."user"
JOIN slack_channels ON slack_messages.channel = slack_channels.id
WHERE slack_users.id = $1
ORDER BY slack_messages.send_at DESC
LIMIT 1
            """,
            user_id,
        )

    data = await request.app["slack_client"].query(url=methods.USERS_INFO, data={"user": user_id})
    api_dump = data["user"]

    response["blocks"] = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Profile information*"}},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*ID:* {api_dump['id']}"},
                {"type": "mrkdwn", "text": f"*Name:* {api_dump['name']}"},
                {"type": "mrkdwn", "text": f"*Real Name:* {api_dump['real_name']}"},
                {
                    "type": "mrkdwn",
                    "text": f"*Display Name:* {api_dump['profile']['display_name']}",
                },
                {"type": "mrkdwn", "text": f"*Email:* {api_dump['profile']['email']}"},
                {"type": "mrkdwn", "text": f"*Deleted:* {api_dump['deleted']}"},
                {"type": "mrkdwn", "text": f"*Timezone:* {api_dump['tz']}"},
                {"type": "mrkdwn", "text": f"*Messages:* {local_dump['total_messages']}"},
                {
                    "type": "mrkdwn",
                    "text": f"*First seen:* {local_dump['first_seen'].isoformat(' ', 'seconds')}",
                },
            ],
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Last message*"}},
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Time:* {local_dump['last_message_ts'].isoformat(' ', 'seconds')}",
                },
                {"type": "mrkdwn", "text": f"*Channel:* {local_dump['last_message_channel']}"},
                {"type": "mrkdwn", "text": f"*Message:* {local_dump['last_message_text']}"},
            ],
        },
    ]

    message = await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)

    response = Message()
    response["channel"] = message["channel"]
    response["thread_ts"] = message["ts"]
    response["blocks"] = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Remove all <@{user_id}> messages ?"},
        },
        {
            "type": "actions",
            "block_id": "inspect",
            "elements": [
                {
                    "type": "button",
                    "action_id": "user_cleanup",
                    "text": {"type": "plain_text", "text": "Do IT !"},
                    "style": "danger",
                    "value": user_id,
                }
            ],
        },
    ]
    await request.app["slack_client"].query(url=methods.CHAT_POST_MESSAGE, data=response)
