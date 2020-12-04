import asyncio
import logging
import datetime
import random

import pytz
import slack
import asyncpg.pool

from slack.io.abc import SlackAPI
from slack.events import Message
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pyslackersweb import models
from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


async def sync_slack_users(slack_client: SlackAPI, pg: asyncpg.pool.Pool,) -> None:
    logger.debug("Refreshing slack users cache.")
    try:
        async with pg.acquire() as conn:
            async for user in slack_client.iter(slack.methods.USERS_LIST, minimum_time=3):
                values = {
                    "deleted": user.get("deleted", False),
                    "admin": user.get("is_admin", False),
                    "bot": user.get("is_bot", False),
                    "timezone": user.get("tz", None),
                }
                await conn.execute(
                    pg_insert(models.SlackUsers)
                    .values(id=user["id"], **values)
                    .on_conflict_do_update(index_elements=[models.SlackUsers.c.id], set_=values)
                )
    except asyncio.CancelledError:
        logger.debug("Slack users cache refresh canceled")
    except Exception:  # pylint: disable=broad-except
        logger.exception("Error refreshing slack users cache")


async def sync_slack_channels(slack_client: SlackAPI, pg: asyncpg.pool.Pool) -> None:
    logger.debug("Refreshing slack channels cache.")

    try:
        async with pg.acquire() as conn:
            async for channel in slack_client.iter(slack.methods.CONVERSATIONS_LIST):
                values = {
                    "name": channel["name"],
                    "created": datetime.datetime.fromtimestamp(channel["created"]),
                    "archived": channel["is_archived"],
                    "members": channel["num_members"],
                    "topic": channel["topic"]["value"],
                    "purpose": channel["purpose"]["value"],
                }
                await conn.execute(
                    pg_insert(models.SlackChannels)
                    .values(id=channel["id"], **values)
                    .on_conflict_do_update(index_elements=[models.SlackChannels.c.id], set_=values)
                )
    except asyncio.CancelledError:
        logger.debug("Slack channels cache refresh canceled")
    except Exception:  # pylint: disable=broad-except
        logger.exception("Error refreshing slack channels cache")


async def advent_of_code(slack_client: SlackAPI) -> None:
    logger.debug("Creating Advent Of Code threads...")

    try:
        for_day = datetime.datetime.now(tz=pytz.timezone("America/New_York"))
        year, day = for_day.year, for_day.day

        # megathread for all solutions at once (most solutions tend to use similar logic)
        message = Message()
        message["channel"] = "advent_of_code"
        message["attachments"] = [
            {
                "fallback": f"Advent Of Code {year} thread for Day {day}",
                "color": random.choice(["#ff0000", "#378b29"]),
                "title": ":santa: :christmas_tree:"
                f" Advent of Code {year}: Day {day}"
                " :christmas_tree: :santa:",
                "title_link": f"https://adventofcode.com/{year}/day/{day}",
                "text": f"Post solutions to day {day} in this thread, in any language!",
                "footer": "Advent of Code",
                "footer_icon": "https://adventofcode.com/favicon.ico",
                "ts": int(for_day.timestamp()),
            }
        ]

        await slack_client.query(slack.methods.CHAT_POST_MESSAGE, data=message)

        # threads for the part1/2 broken out
        for part in range(1, 3):
            message = Message()
            message["channel"] = "advent_of_code"
            message["attachments"] = [
                {
                    "fallback": f"Advent Of Code {year} Thread for Day {day} Part {part}",
                    "color": ["#ff0000", "#378b29"][  # red  # green
                        (part - 1) // 1
                    ],  # red=part 1, green=part 2
                    "title": f"Advent of Code {year}: Day {day} Part {part}",
                    "title_link": f"https://adventofcode.com/{year}/day/{day}",
                    "text": f"Post solutions to part {part} in this thread, in any language!",
                    "footer": "Advent of Code",
                    "footer_icon": "https://adventofcode.com/favicon.ico",
                    "ts": int(for_day.timestamp()),
                }
            ]
            await slack_client.query(slack.methods.CHAT_POST_MESSAGE, data=message)
    except Exception:  # pylint: disable=broad-except
        logger.exception("Failed to create Advent Of Code threads")
