import asyncio
import logging
import datetime

import slack
import asyncpg.pool

from slack.io.abc import SlackAPI
from sqlalchemy.dialects.postgresql import insert as pg_insert

from pyslackersweb import models
from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


async def sync_slack_users(
    slack_client: SlackAPI,
    pg: asyncpg.pool.Pool,
) -> None:
    logger.debug("Refreshing slack users cache.")
    try:
        async with pg.acquire() as conn:
            async for user in slack_client.iter(slack.methods.USERS_LIST, minimum_time=3):
                values = {
                    "name": user["name"],
                    "deleted": user["deleted"],
                    "admin": user["is_admin"],
                    "bot": user["is_bot"],
                    "timezone": user["tz"],
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
