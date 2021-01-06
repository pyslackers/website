import logging

import slack
import asyncpg.pool

from slack.events import Message
from slack.io.abc import SlackAPI

from pyslackersweb.util.log import ContextAwareLoggerAdapter

from . import database

logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


async def post_slack_codewars_challenge(
    slack_client: SlackAPI,
    pg: asyncpg.pool.Pool,
) -> None:
    async with pg.acquire() as conn:
        challenge = await database.get_challenge(conn)

    message = Message()
    message["channel"] = "CEFJ9TJNL"  # advent_of_code
    if challenge:
        message["attachments"] = [
            {
                "fallback": f"Codewars challenge: https://www.codewars.com/kata/{challenge}",
                "color": "#ff0000",
                "title": "Weekly Codewars challenge",
                "title_link": f"https://www.codewars.com/kata/{challenge}",
                "text": "Discuss in this thread",
                "footer": "Codewars",
                "footer_icon": "https://codewars.com/favicon.ico",
            }
        ]
    else:
        message["attachments"] = [
            {
                "fallback": "Codewars challenge: no challenge found",
                "color": "#ff0000",
                "title": "Weekly Codewars challenge",
                "title_link": "https://www.codewars.com",
                "text": "No challenge found :sad-panda:, please seed new challenges ",
                "footer": "Codewars",
                "footer_icon": "https://codewars.com/favicon.ico",
            }
        ]
    await slack_client.query(slack.methods.CHAT_POST_MESSAGE, data=message)
