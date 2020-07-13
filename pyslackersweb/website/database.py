import logging

import asyncpg

from pyslackersweb.util.log import ContextAwareLoggerAdapter


logger = ContextAwareLoggerAdapter(logging.getLogger(__name__))


async def get_user_count(conn: asyncpg.connection.Connection) -> int:
    return await conn.fetchval("SELECT count(id) FROM slack_users")


async def get_timezones(conn: asyncpg.connection.Connection) -> dict:
    timezones = {}
    rows = await conn.fetch("SELECT timezone, count(id) FROM slack_users GROUP BY timezone")
    for row in rows:
        if row["timezone"] is not None:
            timezones[row["timezone"]] = row["count"]

    return timezones
